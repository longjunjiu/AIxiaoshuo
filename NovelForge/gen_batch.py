#!/usr/bin/env python3
"""
NovelForge 批量生成脚本
集成十大经典网文写作技巧
支持 NVIDIA、OpenAI、DeepSeek 等多提供商
"""

import os
import sys
import json
import time
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "skills"))

try:
    from skills.novel_forge.utils.llm_client import LLMClient
except ImportError:
    print("错误: 无法导入 LLMClient，请确保 skills 模块存在")
    sys.exit(1)


WRITING_SYSTEM_PROMPT = """
【十大经典网文写作技巧 - 深度学习】

《斗破苍穹》核心技巧：
- 三年之约：明确目标，读者有期待
- 退婚开局：冲突强，观众有共鸣
- 憋屈→爆发：憋得越久，爆得越爽
- 打脸干脆：不要拖泥带水
- 升级异象：每次突破都有天地异象
- 扮猪吃虎：低调装逼最爽

《凡人修仙传》核心技巧：
- 苟道精髓：不浪、不惹事、但不怕事
- 资源积累：每一步都有收获
- 低调行事：隐藏实力扮猪吃虎
- 稳扎稳打：升级慢热但扎实
- 关键战斗：以弱胜强，靠智取

《诡秘之主》核心技巧：
- 层层悬念：每章都要有谜
- 世界观自洽：设定要完美闭环
- 智斗精彩：斗智斗勇
- 扮演法则：能力越大越要伪装
- 细节伏笔：草蛇灰线，伏脉千里

《雪中悍刀行》核心技巧：
- 群像塑造：每个角色都有故事
- 经典台词：天不生我李淳罡
- 文笔优美：意境深远
- 兄弟情义：有血有肉
- 江湖庙堂：格局宏大

《遮天》核心技巧：
- 九龙拉棺：史诗级开局
- 世界观宏大：宇宙星空
- 荒古圣体：逆天改命
- 帝路争锋：群雄逐鹿
- 伏笔大师：草蛇灰线

《仙逆》核心技巧：
- 顺为凡逆则仙：核心主题
- 为一人逆天：执念驱动
- 凡人流极致：稳扎稳打
- 极境突破：与众不同
- 千年等待：情感至深

《诛仙》核心技巧：
- 情感主线：三段感情纠葛
- 天地不仁：主题深刻
- 人物立体：非黑即白
- 正魔对立：立场冲突
- 悲剧色彩：爱恨交织

《全职高手》核心技巧：
- 专业细节：真实可信
- 团队配合：不是一个人的战斗
- 比赛节奏：紧张刺激
- 人物鲜明：各有特点
- 成长蜕变：从谷底到巅峰

《紫川》核心技巧：
- 幽默与严肃：完美结合
- 群像写法：每个角色都出彩
- 战争描写：大场面精彩
- 反派魅力：不是纯粹邪恶
- 悲剧深刻：动人心魄

【黄金三章法则】

第一章必须完成：
1. 主角出场，让读者认识
2. 抛出核心冲突（退婚/灭门/废物流）
3. 金手指出现或埋下伏笔
4. 章尾留悬念钩子

第二章必须完成：
1. 金手指展示
2. 第一次小试牛刀
3. 建立敌人/目标
4. 埋下更大伏笔

第三章必须完成：
1. 第一个小高潮
2. 解决或部分解决开局冲突
3. 展示主角潜力
4. 建立更大目标

【开局炸弹库】

1. 退婚炸弹
   - 未婚妻当众退婚
   - 主角被嘲讽废物
   - 三年之约立下

2. 灭门炸弹
   - 家族被灭
   - 父母惨死
   - 主角幸存

3. 废物流炸弹
   - 觉醒仪式失败
   - 被测出废物天赋
   - 众人嘲笑

4. 穿越炸弹
   - 穿越到异世界
   - 继承原身记忆
   - 面临困境

5. 逆袭炸弹
   - 最低谷时觉醒
   - 获得上古传承
   - 命运转折

【爽点设计】

小爽点（每章）：
- 打脸成功
- 装逼成功
- 收获资源
- 实力提升

中爽点（每卷）：
- 击败强敌
- 势力扩张
- 情感突破
- 身份揭露

大爽点（全书）：
- 复仇成功
- 登顶巅峰
- 有情人终成眷属
- 世界真相揭露

【语言风格要求】

✅ 好的写法：
- "少爷，你醒了？"清脆的声音传来
- 他攥紧拳头，指节发白
- "你这废物也配？"主角冷笑
- 萧炎没有说话，只是淡淡地看了纳兰嫣然一眼

❌ 禁止的写法：
- "眼中闪过一丝坚定" ❌
- "缓缓地站起身来" ❌
- "天空中乌云密布，仿佛在诉说着什么" ❌
- 大段环境描写开头 ❌
- "他的眼眸中透露出一丝..." ❌
- 主角内心独白超过3句 ❌

【章节结构公式】

1. 开局（前300字）：
   扔炸弹、冲突、危机

2. 发展（中间部分）：
   战斗、对话、推进

3. 高潮（章中段）：
   决战、爆发、转折

4. 结尾（后200字）：
   结果、悬念、新伏笔

请严格按照以上技巧创作。
"""


@dataclass
class NovelConfig:
    title: str = "逆天改命"
    genre: str = "玄幻"
    protagonist_name: str = "叶尘"
    protagonist_age: int = 18
    golden_finger: str = "上古传承"
    world_name: str = "玄元大陆"
    power_system: str = "炼体、炼气、筑基、金丹、元婴"
    main_faction: str = "青云宗"
    enemy_faction: str = "天魔宫"


class BatchNovelGenerator:
    """批量小说生成器"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client
        self.config = NovelConfig()
        self.output_dir = Path("novels")
        self.context = ""
    
    def set_config(self, config: NovelConfig):
        """设置配置"""
        self.config = config
    
    def create_project(self, title: str, genre: str = "玄幻") -> Path:
        """创建项目目录"""
        safe_title = self._sanitize_filename(title)
        project_dir = self.output_dir / safe_title / "volumes/volume_1/chapters"
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        import re
        return re.sub(r'[<>:"/\\|?*]', '', name)
    
    def build_chapter_prompt(self, chapter_num: int, guidance: str = "") -> tuple:
        """构建章节提示词"""
        
        if chapter_num == 1:
            user_prompt = f"""请创作小说《{self.config.title}》第一章。

## 主角信息
- 姓名：{self.config.protagonist_name}
- 年龄：{self.config.protagonist_age}岁
- 背景：原本是大家族少爷，却遭遇巨变

## 世界观
- 世界名称：{self.config.world_name}
- 力量体系：{self.config.power_system}
- 主要势力：{self.config.main_faction}（正派）、{self.config.enemy_faction}（反派）

## 本章要求
1. 【开局炸弹】前300字必须扔出"炸弹"——家族被灭、危机降临
2. 【建立冲突】主角与敌人形成对立
3. 【金手指出现】获得神秘传承（{self.config.golden_finger}）
4. 【章尾钩子】留下悬念，吸引读者继续阅读

{f"## 特别指导\n{guidance}\n" if guidance else ""}

直接输出正文，不要输出任何说明。
字数要求：2500-3000字。
"""
        else:
            user_prompt = f"""请续写小说《{self.config.title}》第{chapter_num}章。

## 主角信息
- 姓名：{self.config.protagonist_name}
- 年龄：{self.config.protagonist_age}岁

## 前章回顾
{self.context[:800] if self.context else '（无前文，自动衔接）'}

## 本章要求
1. 【承接上文】自然衔接前章剧情
2. 【推进剧情】有新的冲突和发展
3. 【爽点设计】设计适当的爽点（打脸、升级、装逼等）
4. 【章尾钩子】留下悬念

{f"## 特别指导\n{guidance}\n" if guidance else ""}

直接输出正文，不要输出任何说明。
字数要求：2500-3000字。
"""
        
        return WRITING_SYSTEM_PROMPT, user_prompt
    
    def generate_chapter(
        self,
        chapter_num: int,
        guidance: str = "",
        temperature: float = 0.8
    ) -> tuple:
        """生成单章"""
        if not self.llm:
            return self._fallback_content(chapter_num), 0.0
        
        system_prompt, user_prompt = self.build_chapter_prompt(chapter_num, guidance)
        
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": user_prompt}],
                system=system_prompt,
                temperature=temperature,
                max_tokens=4000
            )
            
            content = self._post_process_content(response.content, chapter_num)
            
            self.context = content[-1000:] if len(content) > 1000 else content
            
            return content, response.usage.get("completion_tokens", 0) * 0.75
            
        except Exception as e:
            print(f"      错误: {e}")
            return self._fallback_content(chapter_num), 0.0
    
    def _post_process_content(self, content: str, chapter_num: int) -> str:
        """后处理内容"""
        lines = content.strip().split('\n')
        
        title = f"第{chapter_num}章"
        for line in lines[:10]:
            if line.strip().startswith('#'):
                title = line.lstrip('#').strip()
                break
        
        processed = [f"# {title}\n\n"]
        
        skip_patterns = ['```', '以下是', '章节内容', '正文开始', '---']
        started = False
        
        for line in lines:
            stripped = line.strip()
            
            if not started:
                if any(stripped.startswith(p) for p in skip_patterns):
                    continue
                if len(stripped) > 20:
                    started = True
            
            if started:
                processed.append(line)
        
        return '\n'.join(processed)
    
    def _fallback_content(self, chapter_num: int) -> str:
        """备用内容"""
        return f"""# 第{chapter_num}章

（需要API密钥才能生成完整内容）
"""
    
    def batch_generate(
        self,
        start: int,
        end: int,
        title: str = "逆天改命",
        genre: str = "玄幻",
        guidance: str = "",
        checkpoint_interval: int = 5
    ) -> Dict[str, Any]:
        """批量生成"""
        output_dir = self.create_project(title, genre)
        
        results = {
            "total_chapters": 0,
            "successful": 0,
            "failed": 0,
            "total_words": 0,
            "total_time": 0.0,
            "chapters": []
        }
        
        print("\n" + "=" * 60)
        print(f"  NovelForge 批量生成")
        print(f"  书名: {title}")
        print(f"  章节: 第{start}章 - 第{end}章")
        print("=" * 60 + "\n")
        
        for ch in range(start, end + 1):
            results["total_chapters"] += 1
            print(f"📝 生成第{ch}章...")
            
            start_time = time.time()
            
            try:
                content, words = self.generate_chapter(ch, guidance)
                elapsed = time.time() - start_time
                
                output_file = output_dir / f"ch_{ch:03d}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                word_count = len(content.replace(' ', '').replace('\n', ''))
                
                print(f"   ✅ 完成 ({word_count}字, {elapsed:.1f}秒)")
                
                results["successful"] += 1
                results["total_words"] += word_count
                results["total_time"] += elapsed
                results["chapters"].append({
                    "chapter": ch,
                    "word_count": word_count,
                    "time": elapsed,
                    "success": True
                })
                
                if ch % checkpoint_interval == 0:
                    self._save_checkpoint(output_dir, results)
                    print(f"   💾 检查点已保存")
                
            except Exception as e:
                print(f"   ❌ 失败: {e}")
                results["failed"] += 1
                results["chapters"].append({
                    "chapter": ch,
                    "error": str(e),
                    "success": False
                })
            
            time.sleep(0.5)
        
        self._save_summary(output_dir, title, results)
        
        return results
    
    def _save_checkpoint(self, output_dir: Path, results: Dict):
        """保存检查点"""
        checkpoint_file = output_dir / "checkpoint.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def _save_summary(self, output_dir: Path, title: str, results: Dict):
        """保存总结"""
        summary_file = output_dir.parent.parent / "generation_summary.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"《{title}》生成总结\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"总章节数: {results['total_chapters']}\n")
            f.write(f"成功: {results['successful']}\n")
            f.write(f"失败: {results['failed']}\n")
            f.write(f"总字数: {results['total_words']}\n")
            f.write(f"总耗时: {results['total_time']:.1f}秒\n")


def create_llm_client(
    provider: str = "nvidia",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Optional[LLMClient]:
    """创建LLM客户端"""
    
    if not api_key:
        api_key = os.getenv("NVIDIA_API_KEY", "")
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not api_key:
        print("⚠️ 未检测到API密钥，将使用模拟模式")
        return None
    
    from dataclasses import dataclass
    
    @dataclass
    class Config:
        llm_provider: str = provider
        api_key: str = api_key
        base_url: str = ""
        model: str = model or "meta/llama-3.1-70b-instruct"
        temperature: float = 0.7
        max_tokens: int = 4096
    
    try:
        client = LLMClient(Config())
        print(f"✅ LLM客户端已连接 ({provider})")
        return client
    except Exception as e:
        print(f"⚠️ LLM客户端创建失败: {e}")
        return None


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="NovelForge 批量生成")
    parser.add_argument("--start", type=int, default=1, help="起始章节")
    parser.add_argument("--end", type=int, default=10, help="结束章节")
    parser.add_argument("--title", default="逆天改命", help="书名")
    parser.add_argument("--genre", default="玄幻", help="题材")
    parser.add_argument("--provider", default="nvidia", help="LLM提供商")
    parser.add_argument("--guidance", default="", help="全局指导")
    
    args = parser.parse_args()
    
    api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    llm_client = create_llm_client(args.provider, api_key)
    
    generator = BatchNovelGenerator(llm_client)
    
    generator.config = NovelConfig(
        title=args.title,
        genre=args.genre,
        protagonist_name="叶尘",
        protagonist_age=18,
        golden_finger="上古剑典传承",
        world_name="玄元大陆",
        power_system="炼体、炼气、筑基、金丹、元婴、出窍",
        main_faction="青云宗",
        enemy_faction="天魔宫"
    )
    
    results = generator.batch_generate(
        start=args.start,
        end=args.end,
        title=args.title,
        genre=args.genre,
        guidance=args.guidance
    )
    
    print("\n" + "=" * 60)
    print("  生成完成!")
    print("=" * 60)
    print(f"\n📊 统计:")
    print(f"   总章节: {results['total_chapters']}")
    print(f"   成功: {results['successful']}")
    print(f"   失败: {results['failed']}")
    print(f"   总字数: {results['total_words']}")
    print(f"   总耗时: {results['total_time']:.1f}秒")
    print(f"\n📁 输出: novels/{args.title}/")


if __name__ == "__main__":
    main()
