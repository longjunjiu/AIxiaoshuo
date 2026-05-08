"""
写手机器人 - 生成小说正文
参考十大经典网文写作风格
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


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


class WriterAgent:
    """
    写手机器人
    
    参考十大经典网文写作风格：
    - 《斗破苍穹》- 废柴逆袭、爽点密集
    - 《凡人修仙传》- 低调谨慎、稳扎稳打
    - 《诡秘之主》- 悬念迭起、智斗解谜
    - 《雪中悍刀行》- 文笔优美、人物立体
    - 《诛仙》- 情感真实、不狗血
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def get_system_prompt(self) -> str:
        return """你是一位顶尖网络小说作家，精通网文写作技巧。

【十大经典套路 - 网文必备】

1. 废柴逆袭
   主角是废柴 → 被人欺负 → 获得金手指 → 开始逆袭
   《斗破苍穹》萧炎：三年之约，一路逆袭

2. 打脸套路
   被嘲讽 → 隐忍/反驳 → 展现实力 → 打脸 → 获得好处
   经典场景：拍卖会、比武大会、宗门选拔、家族聚会

3. 装逼套路
   低调装逼：扮猪吃虎
   高调装逼：直接展现
   被迫装逼：不得已暴露

4. 金手指系统
   主角必定有一个及以上的金手指
   神器、丹药、传承、系统、老爷爷

5. 收小弟套路
   遇到人才 → 展现实力 → 对方倾佩 → 收为己用

6. 情感线套路
   英雄救美：美女遇险 → 主角出手 → 美女倾心
   日久生情：被迫同行 → 共度患难 → 确立关系

7. 升级突破
   生死战斗突破、机缘巧合突破、服用丹药突破
   天地异象、实力暴涨、境界提升

8. 隐藏身份/马甲梗
   主角马甲非常牛逼，有个牛逼的徒弟但没人知道

9. 扮猪吃虎
   在别人眼里是尊敬羡慕的强人，对主角毕恭毕敬

10. 复仇套路
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

避免的开局：
- ❌ 开篇堆设定（三族五界、修炼等级）
- ❌ 大段环境描写（日落写两页）
- ❌ 视角乱飘

【爽点设计】

爽点类型：
1. 小爽点（每章级别）：打脸、装逼成功
2. 中爽点（每卷高潮）：升级突破、大胜反派
3. 大爽点（全书记忆）：复仇成功、登顶巅峰

爽点密度：
- 每3-5章必须有爽点
- 憋屈后必须有爆发
- 升级要有具体表现

【经典网文风格参考】

《斗破苍穹》（废柴逆袭巅峰）
- 三年之约：目标明确，读者有期待
- 退婚流：开局冲突强
- 升级打怪：节奏明快，爽点密集
- 核心：憋屈→爆发→升级→更强的敌人
- 关键技巧：打脸要干脆利落，憋屈要憋到位

《凡人修仙传》（凡人流开创者）
- 低调谨慎：韩立性格，不浪
- 资源积累：每一步都算计
- 升级慢热：稳扎稳打
- 核心：闷声发大财
- 关键技巧：不要浪，每一步都要有收获

《诡秘之主》（创新派神作）
- 世界观独特：克苏鲁+蒸汽朋克
- 人物塑造：每个角色都有深度
- 悬念设置：层层迷雾，引人入胜
- 核心：智斗解谜
- 关键技巧：世界观要自洽，伏笔要回收

《雪中悍刀行》（文青融合）
- 文笔优美：武侠与玄幻结合
- 人物群像：每个角色都有故事
- 情感细腻：家国情怀、兄弟情义
- 核心：江湖不只是打打杀杀
- 关键技巧：人物要有血有肉，不脸谱化

《诛仙》（仙侠经典）
- 情感主线：张小凡的三段感情
- 世界观：天地不仁，以万物为刍狗
- 人物成长：从平凡到伟大
- 核心：修仙路上的爱恨情仇
- 关键技巧：情感要真实，不狗血

【语言风格】

✅ 好的写法：
- "少爷，你醒了，感觉怎样，没事吧？"稚嫩而清脆的声音如玉珠落盘。
- 他愣愣地看着屋内的一切，迷茫的眼神立时变得精彩之极，震惊，愕然，不可思议...
- "你这废柴也配跟我争？" 主角回怼："很快你就知道谁是废物。"

❌ 避免的写法：
- "眼中闪过一丝坚定的光芒"（太套路）
- "缓缓地"、"骤然"（太书面）
- 大段环境描写
- 主角内心独白太多

【章节结构公式】

高光时刻：写得快、够爽，打怪打脸要干脆
过渡情节：慢一点但别拖沓，赶紧回到主线

请严格按照以上规则进行创作。"""
    
    def build_chapter_prompt(
        self,
        context: WritingContext,
        outline: str,
        previous_chapters: str,
        memory_context: str
    ) -> str:
        return f"""请根据以下信息创作小说章节：

## 基本信息
- 章节标题：{context.chapter_title}
- 章节序号：第{context.chapter_num}章
- 卷号：第{context.volume_num}卷
- 题材：{context.genre}
- 风格：{context.tone}
- 目标字数：{context.target_word_count}字
- 视角：{context.pov}

## 章节大纲
{outline}

## 前文摘要
{previous_chapters}

## 记忆上下文
{memory_context}

## 写作要求

1. 【开局炸弹】
   前300字必须扔出"炸弹"——冲突、危机、悬念

2. 【黄金三章】
   每章必须有冲突、有推进、有期待

3. 【爽点设计】
   根据题材设计适当的爽点（打脸、升级、装逼等）

4. 【悬念钩子】
   章尾留悬念，让读者想追更

5. 【对话自然】
   对话口语化，符合人物性格

6. 【动作描写】
   用动作和表情传达情绪，不直接写心理

7. 【节奏把控】
   高潮部分节奏快，过渡部分不拖沓

请开始创作：
"""
    
    def generate_chapter(
        self,
        context: WritingContext,
        outline: str,
        previous_chapters: str = "",
        memory_context: str = ""
    ) -> str:
        """生成章节内容"""
        if not self.llm:
            return self._generate_fallback_chapter(context, outline)
        
        prompt = self.build_chapter_prompt(
            context=context,
            outline=outline,
            previous_chapters=previous_chapters,
            memory_context=memory_context
        )
        
        response = self.llm.generate(
            system_prompt=self.get_system_prompt(),
            user_prompt=prompt,
            max_tokens=context.target_word_count + 500,
            temperature=0.8
        )
        
        return self._post_process_chapter(response, context)
    
    def _generate_fallback_chapter(
        self,
        context: WritingContext,
        outline: str
    ) -> str:
        """当没有LLM时的备用生成"""
        return f"""# {context.chapter_title}

（系统提示：需要配置LLM才能生成完整内容）

章节要求：
- 目标字数：{context.target_word_count}字
- 题材：{context.genre}
- 风格：{context.tone}

请配置API密钥后重新生成。
"""
    
    def _post_process_chapter(self, content: str, context: WritingContext) -> str:
        """后处理章节内容"""
        lines = content.strip().split('\n')
        
        if lines[0].startswith('#'):
            title = lines[0].lstrip('#').strip()
        else:
            title = context.chapter_title
        
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
    
    def batch_write_chapters(
        self,
        contexts: List[WritingContext],
        outlines: List[str],
        previous_chapters: str = "",
        memory_context: str = ""
    ) -> List[str]:
        """批量生成章节"""
        chapters = []
        
        for i, (context, outline) in enumerate(zip(contexts, outlines)):
            if i > 0:
                prev_summary = self._summarize_chapter(chapters[i-1])
                previous_chapters = f"上一章摘要：{prev_summary}\n\n{previous_chapters}"
            
            chapter = self.generate_chapter(
                context=context,
                outline=outline,
                previous_chapters=previous_chapters,
                memory_context=memory_context
            )
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
