#!/usr/bin/env python3
"""NVIDIA API小说生成器"""
import os
import sys
import json
import time
import requests
from pathlib import Path

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
if not NVIDIA_API_KEY:
    print("❌ 需要设置 NVIDIA_API_KEY")
    sys.exit(1)

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-3.1-70b-instruct"

SYSTEM_PROMPT = """你是一个专业的网络小说作家，擅长创作玄幻修仙类小说。

写作风格要求：
1. 文笔流畅，叙事生动，有画面感
2. 人物对话符合性格，有特色
3. 情节推进自然，有爽点
4. 适当的环境描写和心理描写
5. 参考《斗破苍穹》《凡人修仙传》的写作风格"""

USER_PROMPT = """请为小说《星辰剑影》创作第一章。

背景设定：
- 主角：陈墨，18岁，陈家遗孤
- 世界：修仙世界
- 宗门：青云宗
- 金手指：星辰剑典（神秘的剑道传承）
- 核心冲突：灭门复仇

本章要求：
1. 开篇要吸引人
2. 主角处于困境但有希望的伏笔
3. 展示主角的性格特点
4. 结尾要有悬念

请直接输出正文。"""

def generate(prompt, max_tokens=2048):
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": max_tokens
    }
    resp = requests.post(API_URL, headers=headers, json=data, timeout=120)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

def main():
    print("=" * 60)
    print("  NovelForge × NVIDIA NIM 小说生成")
    print("=" * 60)

    # 生成第一章
    print("\n📝 生成第一章...")
    start = time.time()
    ch1 = generate(f"{USER_PROMPT}\n\n（第一部分：开篇，500字）", max_tokens=800)
    ch2 = generate(f"续写上文，承接主角获得传承的剧情，继续发展故事（500字）", max_tokens=800)
    ch3 = generate(f"续写上文，主角面临的危机和困境（500字）", max_tokens=800)
    ch4 = generate(f"续写上文，结尾悬念（300字）", max_tokens=500)

    content = ch1 + "\n\n" + ch2 + "\n\n" + ch3 + "\n\n" + ch4
    elapsed = time.time() - start

    print(f"\n✅ 生成完成！耗时: {elapsed:.1f}秒")
    print(f"   总字数: {len(content)}")

    # 保存
    output_dir = Path("novels/星辰剑影_正文/volumes/volume_1/chapters")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "ch_001.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 第1章 命运的转折\n\n{content}")

    print(f"\n📁 已保存: {output_file}")

    print("\n" + "=" * 60)
    print("  内容预览")
    print("=" * 60)
    print(content[:600])
    print("\n...")

if __name__ == "__main__":
    main()
