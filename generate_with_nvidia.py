#!/usr/bin/env python3
"""
使用NVIDIA API调用MiniMax模型生成小说正文
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "skills"))

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

if not NVIDIA_API_KEY:
    print("❌ 需要设置 NVIDIA_API_KEY 环境变量")
    print("   获取地址: https://build.nvidia.com/explore/discover")
    sys.exit(1)

os.environ["NVIDIA_API_KEY"] = NVIDIA_API_KEY

from skills.novel_forge.utils.llm_client import LLMClient
from dataclasses import dataclass

@dataclass
class ForgeConfig:
    llm_provider: str = "nvidia"
    api_key: str = ""
    base_url: str = "https://integrate.api.nvidia.com/v1"
    model: str = "meta/llama-3.1-70b-instruct"
    temperature: float = 0.7
    max_tokens: int = 4096

def main():
    print("=" * 70)
    print("  NovelForge × NVIDIA × MiniMax-2.7 小说正文生成")
    print("=" * 70)

    config = ForgeConfig()

    project_path = Path("novels/星辰剑影_正文")
    project_path.mkdir(parents=True, exist_ok=True)

    print(f"\n📚 项目: 星辰剑影")
    print(f"   模型: {config.model}")
    print(f"   路径: {project_path}")

    print("\n" + "=" * 70)
    print("  生成第一章")
    print("=" * 70)

    system_prompt = """你是一个专业的网络小说作家，擅长创作玄幻修仙类小说。

写作风格要求：
1. 文笔流畅，叙事生动，有画面感
2. 人物对话符合性格，有特色
3. 情节推进自然，有爽点
4. 适当的环境描写和心理描写
5. 每章3000字左右

参考《斗破苍穹》《凡人修仙传》的写作风格。"""

    user_prompt = """请为小说《星辰剑影》创作第一章。

背景设定：
- 主角：陈墨，18岁，陈家遗孤
- 世界：修仙世界
- 宗门：青云宗
- 金手指：星辰剑典（神秘的剑道传承）
- 核心冲突：灭门复仇

本章要求：
1. 开篇要吸引人，设定世界观
2. 主角处于困境但有希望的伏笔
3. 展示主角的性格特点
4. 结尾要有悬念

请直接输出正文，不需要章节标题。"""

    print("\n正在调用NVIDIA API (MiniMax-2.7) 生成正文...")
    print("-" * 50)

    start_time = time.time()

    try:
        llm = LLMClient(config)

        messages = [
            {"role": "user", "content": user_prompt}
        ]

        response = llm.chat(
            messages=messages,
            system=system_prompt,
            temperature=0.8,
            max_tokens=4096
        )

        elapsed = time.time() - start_time

        content = response.content

        print(f"\n✅ 生成完成！耗时: {elapsed:.1f}秒")
        print(f"   字符数: {len(content)}")

        print("\n" + "=" * 70)
        print("  生成内容预览")
        print("=" * 70)
        preview = content[:800] if len(content) > 800 else content
        print(preview)
        print("\n...")

        ch_path = project_path / "volumes/volume_1/chapters"
        ch_path.mkdir(parents=True, exist_ok=True)

        output_file = ch_path / "ch_001.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 第1章 命运的转折\n\n{content}")

        print(f"\n📁 已保存到: {output_file}")

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
