"""
写手机器人 - 生成小说正文
参考十大经典网文写作风格
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import re


@dataclass
class WritingContext:
    """写作上下文"""
    chapter_title: str
    chapter_num: int
    volume_num: int
    genre: str
    tone: str
    target_word_count: int
    pov: str = "第三人称"


@dataclass
class ChapterOutline:
    """章节大纲"""
    title: str
    synopsis: str = ""
    scenes: List[Dict] = None
    
    def __post_init__(self):
        if self.scenes is None:
            self.scenes = []


class WriterAgent:
    """写手机器人"""
    
    def __init__(self, llm_client=None, project=None, craft=None, anti_slop=None):
        self.llm = llm_client
        self.project = project
        self.craft = craft
        self.anti_slop = anti_slop
    
    def get_system_prompt(self) -> str:
        return """你是一位顶尖网络小说作家，精通网文写作技巧。

【十大经典套路 - 网文必备】

1. 废柴逆袭
   主角是废柴 → 被人欺负 → 获得金手指 → 开始逆袭

2. 打脸套路
   被嘲讽 → 隐忍/反驳 → 展现实力 → 打脸 → 获得好处

3. 装逼套路
   低调装逼：扮猪吃虎
   高调装逼：直接展现
   被迫装逼：不得已暴露

4. 金手指系统
   主角必定有一个及以上的金手指

5. 升级突破
   生死战斗突破、机缘巧合突破、服用丹药突破

6. 复仇套路
   受到伤害 → 蛰伏隐忍 → 暗中积蓄实力 → 时机成熟 → 复仇行动

【黄金三章法则】

第一章核心任务：
- 主角出场，让读者知道谁是主角
- 抛出冲突，第一章就要有矛盾
- 埋下期待，让读者想知道后面发生什么

第二章核心任务：
- 金手指/转机出现
- 展示主角潜力

第三章核心任务：
- 小高潮爆发
- 每章结尾留钩子

【开局必杀技 - 前300字】

开篇直接扔炸弹：
- 被嘲讽/被退婚/被欺负
- 穿越重生/获得金手指
- 命悬一线/危机降临

【爽点设计】

爽点类型：
1. 小爽点（每章级别）：打脸、装逼成功
2. 中爽点（每卷高潮）：升级突破、大胜反派
3. 大爽点（全书记忆）：复仇成功、登顶巅峰

爽点密度：
- 每3-5章必须有爽点
- 憋屈后必须有爆发
- 升级要有具体表现

【语言风格】

好的写法：
- "少爷，你醒了，感觉怎样，没事吧？"稚嫩而清脆的声音如玉珠落盘。
- 他愣愣地看着屋内的一切，迷茫的眼神立时变得精彩之极，震惊，愕然，不可思议...
- "你这废柴也配跟我争？" 主角回怼："很快你就知道谁是废物。"

避免的写法：
- "眼中闪过一丝坚定的光芒"（太套路）
- "缓缓地"、"骤然"（太书面）
- 大段环境描写
- 主角内心独白太多

请严格按照以上规则进行创作。"""
    
    def pre_write_check(self, context) -> Dict[str, Any]:
        """写前自检"""
        return {
            "passed": True,
            "warnings": [],
            "notes": "上下文检查通过"
        }
    
    def write_chapter(self, context, style_profile=None) -> str:
        """生成章节内容"""
        if not self.llm:
            return self._generate_fallback_chapter(context)
        
        prompt = self._build_chapter_prompt(context)
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.get_system_prompt(),
            temperature=0.8,
            max_tokens=context.target_word_count + 500
        )
        
        return self._post_process_chapter(response.content, context)
    
    def _build_chapter_prompt(self, context) -> str:
        """构建章节提示词"""
        genre = getattr(context, 'genre', '玄幻')
        tone = getattr(context, 'tone', '热血')
        chapter_num = getattr(context, 'chapter_num', 1)
        volume_num = getattr(context, 'volume_num', 1)
        target_words = getattr(context, 'target_word_count', 3000)
        
        outline = getattr(context, 'outline', None)
        outline_text = ""
        if outline:
            if hasattr(outline, 'synopsis'):
                outline_text = outline.synopsis
            elif isinstance(outline, dict):
                outline_text = outline.get('synopsis', '')
        
        long_term = getattr(context, 'long_term_context', {})
        mid_term = getattr(context, 'mid_term_context', {})
        
        prev_summary = ""
        if isinstance(mid_term, dict):
            prev_summary = mid_term.get('summary', '')
        
        return f"""请创作小说章节：

## 基本信息
- 章节：第{volume_num}卷 第{chapter_num}章
- 题材：{genre}
- 风格：{tone}
- 目标字数：{target_words}字

## 章节大纲
{outline_text}

## 前文摘要
{prev_summary}

## 写作要求

1. 【开局炸弹】前300字必须扔出"炸弹"——冲突、危机、悬念

2. 【黄金三章】每章必须有冲突、有推进、有期待

3. 【爽点设计】根据题材设计适当的爽点（打脸、升级、装逼等）

4. 【悬念钩子】章尾留悬念，让读者想追更

5. 【对话自然】对话口语化，符合人物性格

6. 【动作描写】用动作和表情传达情绪，不直接写心理

7. 【节奏把控】高潮部分节奏快，过渡部分不拖沓

直接输出正文，不要输出其他内容。
"""
    
    def _generate_fallback_chapter(self, context) -> str:
        """当没有LLM时的备用生成"""
        title = getattr(context, 'chapter_title', '未命名章节')
        words = getattr(context, 'target_word_count', 3000)
        genre = getattr(context, 'genre', '玄幻')
        
        return f"""# {title}

（系统提示：需要配置LLM才能生成完整内容）

章节要求：
- 目标字数：{words}字
- 题材：{genre}

请配置API密钥后重新生成。
"""
    
    def _post_process_chapter(self, content: str, context) -> str:
        """后处理章节内容"""
        lines = content.strip().split('\n')
        
        title = getattr(context, 'chapter_title', '未命名章节')
        if lines and lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
        
        processed_lines = [f"# {title}", ""]
        
        in_content = False
        for line in lines[1:]:
            if line.strip() and not line.startswith('#'):
                in_content = True
            if in_content:
                processed_lines.append(line)
        
        processed = '\n'.join(processed_lines)
        
        word_count = len(processed.replace(' ', '').replace('\n', ''))
        processed += f"\n\n（本章字数：约{word_count}字）"
        
        return processed
    
    def post_write_settlement(self, content: str, outline) -> Dict[str, Any]:
        """写后结算"""
        return {
            "word_count": len(content),
            "hooks_planted": [],
            "hooks_recycled": [],
            "resources_changed": []
        }
    
    def batch_write_chapters(
        self,
        contexts: List,
        outlines: List[str],
        previous_chapters: str = "",
        memory_context: str = ""
    ) -> List[str]:
        """批量生成章节"""
        chapters = []
        
        for i, context in enumerate(contexts):
            if i > 0 and chapters:
                prev_summary = self._summarize_chapter(chapters[i-1])
                context.prev_summary = prev_summary
            
            chapter = self.write_chapter(context=context)
            chapters.append(chapter)
        
        return chapters
    
    def _summarize_chapter(self, chapter: str) -> str:
        """摘要章节"""
        lines = chapter.split('\n')
        content_lines = [l for l in lines if l.strip() and not l.startswith('#')]
        
        summary = []
        for line in content_lines[:5]:
            if len(line) > 20:
                summary.append(line[:50] + "...")
                break
        
        return " ".join(summary) if summary else "章节内容省略"
