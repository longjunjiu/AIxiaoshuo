"""
测试脚本 - 无 LLM 模式下跑完整流程
用来验证系统骨架是否正常，章节用占位文本。
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "skills"))

from skills.novel_forge import NovelForge, ForgeConfig
from skills.novel_forge.agents.writer import WritingContext


# ── 配置 ──────────────────────────────────────────────────────
TITLE    = "星河战纪"
GENRE    = "xuanhuan"
SYNOPSIS = "少年叶星河在家族被灭之际，意外觉醒上古战神血脉，开始了逆天改命的征途。"
CHAPTERS = 5       # 测试生成章节数
WORDS    = 2000    # 每章目标字数
OUTPUT   = "./novels"

# 如果配置了真实 API Key，改为 True 使用 LLM
USE_LLM  = bool(os.getenv("OPENAI_API_KEY") or
               os.getenv("ANTHROPIC_API_KEY") or
               os.getenv("API_KEY"))


def force_fallback(forge: NovelForge):
    """强制禁用 LLM，所有 Agent 走静态降级路径"""
    forge.orchestrator.architect.llm = None
    forge.orchestrator.writer.llm    = None
    forge.orchestrator.auditor.llm   = None
    forge.orchestrator.reviser.llm   = None
    forge.orchestrator.panel.llm     = None
    forge.orchestrator.long_term.project  # ensure loaded
    print("  [降级模式] 所有 Agent 已切换为静态降级路径\n")


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def main():
    section("NovelForge 系统测试")

    # ── 1. 初始化 ──────────────────────────────────────────────
    config = ForgeConfig(
        llm_provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model="gpt-4",
        temperature=0.75,
        max_tokens=4096,
    )
    forge = NovelForge(config)

    if not USE_LLM:
        print("\n未检测到 API Key，切换为【静态降级模式】")
        print("如需使用真实 LLM，请设置环境变量：")
        print("  export OPENAI_API_KEY=sk-xxxxx")
        print("  export LLM_PROVIDER=openai")

    # ── 2. 创建项目 ────────────────────────────────────────────
    section("步骤 1/6  创建项目")
    project = forge.create_project(
        title=TITLE,
        genre=GENRE,
        synopsis=SYNOPSIS,
        target_chapters=CHAPTERS,
        target_words_per_chapter=WORDS,
        output_dir=OUTPUT,
    )
    print(f"  书名：{project.title}")
    print(f"  题材：{project.genre}")
    print(f"  路径：{project.project_path}")

    if not USE_LLM:
        force_fallback(forge)

    # ── 3. 生成设定 ────────────────────────────────────────────
    section("步骤 2/6  生成世界观 / 角色设定")
    settings = forge.generate_settings(themes=["复仇", "热血", "成长"])
    for k, v in settings.items():
        preview = v.split("\n")[0].replace("# ", "")
        print(f"  [{k}]  {preview}  ({len(v)} 字符)")

    # ── 4. 生成大纲 ────────────────────────────────────────────
    section("步骤 3/6  生成全书大纲")
    outline_path = forge.generate_outline(num_volumes=3, chapters_per_volume=30)
    print(f"  大纲文件：{outline_path}")

    # ── 5. 批量写作 ────────────────────────────────────────────
    section(f"步骤 4/6  写作前 {CHAPTERS} 章（多 Agent 协作）")
    results = []
    for ch in range(1, CHAPTERS + 1):
        print(f"\n── 第 {ch} 章 ──")
        result = forge.write_chapter(
            chapter_num=ch,
            volume_num=1,
            guidance="" if ch > 1 else "第一章要有震撼开局，展示主角金手指",
            max_revisions=1,
        )
        results.append(result)
        status = "✅ 通过" if result.get("success") else "⚠ 降级"
        print(f"  {status}  字数:{result.get('word_count',0):>6}  "
              f"迭代:{len(result.get('iterations',[]))}")

    # ── 6. 审计一章 ────────────────────────────────────────────
    section("步骤 5/6  审计第 1 章")
    audit = forge.audit_chapter(chapter_num=1)
    print(f"  评分：{audit.get('score', 0):.1f} / 100")
    print(f"  通过：{'✅' if audit.get('pass') else '❌'}")
    print(f"  AI 特征：{audit.get('ai_tells', {}).get('severity', 'N/A')}")
    if audit.get("issues"):
        for i in audit["issues"][:3]:
            print(f"  - {i}")

    # ── 7. 修订一章 ────────────────────────────────────────────
    section("步骤 5/6  修订第 1 章（polish 模式）")
    revision = forge.revise_chapter(chapter_num=1, mode="polish")
    print(f"  成功：{'✅' if revision.get('success') else '❌'}")
    print(f"  修改：{revision.get('changes', [])}")

    # ── 8. 伏笔追踪 ────────────────────────────────────────────
    section("步骤 6/6  项目状态 & 伏笔追踪")
    status = forge.get_status()
    print(f"  书名       ：{status['title']}")
    print(f"  已写章节   ：{status['written_chapters']} / {status['total_chapters']}")
    print(f"  总字数     ：{status['word_count']:,}")
    print(f"  待回收伏笔 ：{status['pending_hooks']}")

    hooks = forge.track_hooks()
    print(f"\n  伏笔总计：{hooks.get('total', 0)}")
    if hooks.get("pending_hooks"):
        for h in hooks["pending_hooks"][:3]:
            print(f"  · [{h['id']}] {str(h.get('content',''))[:40]}")

    # ── 9. 导出 ────────────────────────────────────────────────
    section("导出书稿")
    export_path = forge.export_book(format="markdown")
    size = Path(export_path).stat().st_size if Path(export_path).exists() else 0
    print(f"  路径：{export_path}")
    print(f"  大小：{size:,} 字节")

    # ── 汇总 ────────────────────────────────────────────────────
    section("测试完成")
    success = sum(1 for r in results if r.get("success"))
    print(f"  章节通过率：{success}/{CHAPTERS}")
    print(f"  总字数    ：{status['word_count']:,}")
    print(f"  模式      ：{'LLM生成' if USE_LLM else '静态降级（占位文本）'}")
    print("\n  项目目录：")
    for p in sorted(Path(project.project_path).rglob("*.md"))[:12]:
        rel = p.relative_to(project.project_path)
        print(f"    {rel}")

    print(f"\n  [完成] 书稿位于：{project.project_path}")


if __name__ == "__main__":
    main()
