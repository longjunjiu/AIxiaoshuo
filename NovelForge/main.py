"""
NovelForge CLI - 命令行入口
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "skills"))

from skills.novel_forge import NovelForge, ForgeConfig


def load_config(config_path: Optional[str] = None) -> ForgeConfig:
    """加载配置"""
    if config_path and Path(config_path).exists():
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return ForgeConfig(**data)
    
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
    
    return ForgeConfig(
        llm_provider="openai" if "OPENAI" in os.getenv("LLM_PROVIDER", "") else "anthropic",
        api_key=api_key,
        model=os.getenv("LLM_MODEL", "gpt-4"),
        temperature=0.7,
        max_tokens=4096
    )


def cmd_create(args):
    """创建新书"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    project = forge.create_project(
        title=args.title,
        genre=args.genre,
        synopsis=args.synopsis,
        target_chapters=args.chapters,
        target_words_per_chapter=args.words,
        output_dir=args.output
    )
    
    print(f"✅ 已创建项目: {project.title}")
    print(f"   路径: {project.project_path}")
    print(f"   题材: {project.genre}")
    print(f"   目标章节: {project.target_chapters}")


def cmd_generate_settings(args):
    """生成设定"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    if not args.project:
        print("❌ 请指定项目路径 (--project)")
        return
    
    forge.load_project(args.project)
    
    settings = forge.generate_settings(
        themes=args.themes.split(',') if args.themes else None
    )
    
    print("✅ 设定生成完成")
    for key, content in settings.items():
        print(f"   - {key}: {len(content)} 字符")


def cmd_generate_outline(args):
    """生成大纲"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    if not args.project:
        print("❌ 请指定项目路径 (--project)")
        return
    
    forge.load_project(args.project)
    
    outline_path = forge.generate_outline(
        num_volumes=args.volumes,
        chapters_per_volume=args.chapters_per_volume
    )
    
    print(f"✅ 大纲生成完成")
    print(f"   路径: {outline_path}")


def cmd_write(args):
    """写作章节"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    if not args.project:
        print("❌ 请指定项目路径 (--project)")
        return
    
    forge.load_project(args.project)
    
    result = forge.write_chapter(
        chapter_num=args.chapter,
        volume_num=args.volume,
        guidance=args.guidance or "",
        auto_audit=not args.no_audit,
        auto_revise=not args.no_revise,
        max_revisions=args.max_revisions
    )
    
    if result.get("success"):
        print(f"✅ 第{args.chapter}章写作完成")
        print(f"   字数: {result.get('word_count', 0)}")
        print(f"   修订轮数: {len(result.get('revisions', []))}")
    else:
        print(f"❌ 第{args.chapter}章写作失败")


def cmd_batch_write(args):
    """批量写作"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    if not args.project:
        print("❌ 请指定项目路径 (--project)")
        return
    
    forge.load_project(args.project)
    
    print(f"开始批量写作: 第{args.start}章 - 第{args.end}章")
    
    results = forge.batch_write(
        start_chapter=args.start,
        end_chapter=args.end,
        volume_num=args.volume,
        checkpoint_interval=args.checkpoint
    )
    
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n✅ 批量写作完成")
    print(f"   成功: {success_count}/{len(results)}")


def cmd_audit(args):
    """审计章节"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    if not args.project:
        print("❌ 请指定项目路径 (--project)")
        return
    
    forge.load_project(args.project)
    
    result = forge.audit_chapter(
        chapter_num=args.chapter,
        volume_num=args.volume
    )
    
    print(f"📊 审计报告 - 第{args.chapter}章")
    print(f"   通过: {'✅' if result.get('pass') else '❌'}")
    print(f"   分数: {result.get('scores', {}).get('overall', 0):.1f}/10")
    
    if result.get("issues"):
        print(f"\n   严重问题: {len(result['issues'])}")
        for issue in result["issues"][:3]:
            print(f"   - [{issue.get('dimension')}] {issue.get('message', '')[:50]}")
    
    if result.get("warnings"):
        print(f"\n   警告: {len(result['warnings'])}")


def cmd_detect_aigc(args):
    """AIGC检测"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    if not args.project:
        print("❌ 请指定项目路径 (--project)")
        return
    
    forge.load_project(args.project)
    
    result = forge.detect_aigc(
        chapter_num=args.chapter,
        volume_num=args.volume,
        full_novel=args.full
    )
    
    if args.full:
        print(f"📊 全书AIGC检测报告")
        print(f"   总章节: {result.get('total_chapters', 0)}")
        print(f"   整体风险: {result.get('overall_risk', 'UNKNOWN')}")
        print(f"   高风险: {result.get('risk_distribution', {}).get('high', 0)}")
        print(f"   中风险: {result.get('risk_distribution', {}).get('medium', 0)}")
        print(f"   低风险: {result.get('risk_distribution', {}).get('low', 0)}")
    else:
        print(f"📊 AIGC检测报告 - 第{args.chapter}章")
        print(f"   风险等级: {result.get('risk_level', 'UNKNOWN')}")
        print(f"   Tier1问题: {result.get('tier1_count', 0)}")
        print(f"   Tier2聚类: {result.get('tier2_clusters', 0)}")
        
        if result.get("suggestions"):
            print(f"\n   建议:")
            for s in result["suggestions"][:3]:
                print(f"   - {s}")


def cmd_track_hooks(args):
    """伏笔追踪"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    if not args.project:
        print("❌ 请指定项目路径 (--project)")
        return
    
    forge.load_project(args.project)
    
    status = forge.track_hooks()
    
    print(f"📊 伏笔追踪状态")
    print(f"   总计: {status.get('total', 0)}")
    print(f"   待回收: {status.get('pending_count', 0)}")
    print(f"   已回收: {status.get('recycled_count', 0)}")
    print(f"   回收率: {status.get('recycle_rate', 0):.1%}")
    
    if status.get("pending_hooks"):
        print(f"\n   待回收伏笔 (前5):")
        for hook in status["pending_hooks"][:5]:
            print(f"   - [{hook['id']}] {hook['content'][:40]}...")


def cmd_status(args):
    """查看状态"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    if not args.project:
        print("❌ 请指定项目路径 (--project)")
        return
    
    forge.load_project(args.project)
    
    status = forge.get_status()
    
    print(f"📚 项目状态")
    print(f"   书名: {status.get('title', 'N/A')}")
    print(f"   题材: {status.get('genre', 'N/A')}")
    print(f"   已写章节: {status.get('written_chapters', 0)}/{status.get('total_chapters', 0)}")
    print(f"   总字数: {status.get('word_count', 0):,}")
    print(f"   待回收伏笔: {status.get('pending_hooks', 0)}")
    print(f"   路径: {status.get('project_path', 'N/A')}")


def cmd_export(args):
    """导出书籍"""
    config = load_config(args.config)
    forge = NovelForge(config)
    
    if not args.project:
        print("❌ 请指定项目路径 (--project)")
        return
    
    forge.load_project(args.project)
    
    output_path = forge.export_book(format=args.format)
    
    print(f"✅ 导出完成")
    print(f"   路径: {output_path}")
    print(f"   格式: {args.format}")


def main():
    parser = argparse.ArgumentParser(
        description="NovelForge - AI小说辅助创作技能",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--config", "-c", help="配置文件路径")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    create_parser = subparsers.add_parser("create", help="创建新书")
    create_parser.add_argument("--title", "-t", required=True, help="书名")
    create_parser.add_argument("--genre", "-g", required=True, help="题材")
    create_parser.add_argument("--synopsis", "-s", required=True, help="简介")
    create_parser.add_argument("--chapters", type=int, default=1000, help="目标章节数")
    create_parser.add_argument("--words", type=int, default=3000, help="每章目标字数")
    create_parser.add_argument("--output", "-o", default="./novels", help="输出目录")
    
    settings_parser = subparsers.add_parser("settings", help="生成设定")
    settings_parser.add_argument("--project", "-p", required=True, help="项目路径")
    settings_parser.add_argument("--themes", help="核心主题(逗号分隔)")
    
    outline_parser = subparsers.add_parser("outline", help="生成大纲")
    outline_parser.add_argument("--project", "-p", required=True, help="项目路径")
    outline_parser.add_argument("--volumes", type=int, default=10, help="卷数")
    outline_parser.add_argument("--chapters-per-volume", type=int, default=100, help="每卷章节数")
    
    write_parser = subparsers.add_parser("write", help="写作章节")
    write_parser.add_argument("--project", "-p", required=True, help="项目路径")
    write_parser.add_argument("--chapter", type=int, required=True, help="章节号")
    write_parser.add_argument("--volume", type=int, default=1, help="卷号")
    write_parser.add_argument("--guidance", help="章节指导")
    write_parser.add_argument("--no-audit", action="store_true", help="跳过审计")
    write_parser.add_argument("--no-revise", action="store_true", help="跳过修订")
    write_parser.add_argument("--max-revisions", type=int, default=3, help="最大修订轮数")
    
    batch_parser = subparsers.add_parser("batch", help="批量写作")
    batch_parser.add_argument("--project", "-p", required=True, help="项目路径")
    batch_parser.add_argument("--start", type=int, required=True, help="起始章节")
    batch_parser.add_argument("--end", type=int, required=True, help="结束章节")
    batch_parser.add_argument("--volume", type=int, default=1, help="卷号")
    batch_parser.add_argument("--checkpoint", type=int, default=5, help="检查点间隔")
    
    audit_parser = subparsers.add_parser("audit", help="审计章节")
    audit_parser.add_argument("--project", "-p", required=True, help="项目路径")
    audit_parser.add_argument("--chapter", type=int, required=True, help="章节号")
    audit_parser.add_argument("--volume", type=int, default=1, help="卷号")
    
    detect_parser = subparsers.add_parser("detect", help="AIGC检测")
    detect_parser.add_argument("--project", "-p", required=True, help="项目路径")
    detect_parser.add_argument("--chapter", type=int, help="章节号")
    detect_parser.add_argument("--volume", type=int, default=1, help="卷号")
    detect_parser.add_argument("--full", action="store_true", help="检测全书")
    
    hooks_parser = subparsers.add_parser("hooks", help="伏笔追踪")
    hooks_parser.add_argument("--project", "-p", required=True, help="项目路径")
    
    status_parser = subparsers.add_parser("status", help="查看状态")
    status_parser.add_argument("--project", "-p", required=True, help="项目路径")
    
    export_parser = subparsers.add_parser("export", help="导出书籍")
    export_parser.add_argument("--project", "-p", required=True, help="项目路径")
    export_parser.add_argument("--format", "-f", choices=["markdown", "text", "json"], default="markdown", help="导出格式")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        "create": cmd_create,
        "settings": cmd_generate_settings,
        "outline": cmd_generate_outline,
        "write": cmd_write,
        "batch": cmd_batch_write,
        "audit": cmd_audit,
        "detect": cmd_detect_aigc,
        "hooks": cmd_track_hooks,
        "status": cmd_status,
        "export": cmd_export
    }
    
    cmd = commands.get(args.command)
    if cmd:
        cmd(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
