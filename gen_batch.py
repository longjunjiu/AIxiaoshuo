#!/usr/bin/env python3
"""NVIDIA API小说生成器 - 多章节批量生成"""
import os
import json
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-3.1-70b-instruct"

def generate_novel_content(chapter_num, context=""):
    """生成单章内容"""
    system_prompt = """你是一个网络小说作家，擅长玄幻修仙题材。

重要规则：
1. 主角名字固定为"陈墨"，不要换成其他名字
2. 保持剧情连贯，每章3000字
3. 文笔流畅，对话自然
4. 参考《斗破苍穹》风格"""

    if chapter_num == 1:
        user_prompt = """创作《星辰剑影》第一章。

设定：
- 主角：陈墨，18岁，家族被灭门的少年
- 宗门：青云宗
- 金手指：星辰剑典（神秘传承）

要求：
1. 开篇：灭门之夜，陈墨幸存
2. 获得星辰剑典传承
3. 被追杀，逃往青云宗
4. 结尾悬念

直接输出正文。"""
    else:
        prev = context if context else "上章剧情"
        user_prompt = f"""续写《星辰剑影》第{chapter_num}章。

上章回顾：{prev}

本章要求：
1. 承接上文剧情
2. 主角固定是陈墨
3. 3000字左右
4. 有冲突和发展

直接输出正文。"""

    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2500
    }

    start = time.time()
    resp = requests.post(API_URL, headers=headers, json=data, timeout=180)
    resp.raise_for_status()
    elapsed = time.time() - start

    return resp.json()["choices"][0]["message"]["content"], elapsed

def main():
    print("=" * 60)
    print("  NovelForge × NVIDIA NIM 批量生成")
    print("=" * 60)

    output_dir = Path("novels/星辰剑影_正文/volumes/volume_1/chapters")
    output_dir.mkdir(parents=True, exist_ok=True)

    total_words = 0
    total_time = 0
    context = ""

    # 生成10章
    for ch in range(1, 11):
        print(f"\n📝 生成第{ch}章...")
        try:
            content, elapsed = generate_novel_content(ch, context)
            total_time += elapsed
            total_words += len(content)

            # 保存
            output_file = output_dir / f"ch_{ch:03d}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# 第{ch}章\n\n{content}")

            print(f"   ✅ 完成! ({len(content)}字, {elapsed:.1f}秒)")

            # 更新上下文
            context = content[-500:] if len(content) > 500 else content

        except Exception as e:
            print(f"   ❌ 失败: {e}")
            break

    print("\n" + "=" * 60)
    print("  生成完成!")
    print("=" * 60)
    print(f"\n📊 统计:")
    print(f"   总章节: 10")
    print(f"   总字数: {total_words}")
    print(f"   总耗时: {total_time:.1f}秒")
    print(f"\n📁 输出: {output_dir}")

if __name__ == "__main__":
    main()
