"""
建筑师机器人 - 规划小说结构和章节大纲
参考十大经典网文结构设计
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


class ArchitectAgent:
    """建筑师机器人"""
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def get_system_prompt(self) -> str:
        return """你是一位顶尖网络小说大纲规划师，精通网文结构设计。

【十大经典网文结构参考】

《斗破苍穹》结构：
- 开局：废柴被退婚，三年之约立下
- 发展：升级打怪，获得异火
- 高潮：三年期满，约战成功
- 核心节奏：憋屈→爆发→升级→更强的敌人→再爆发

《凡人修仙传》结构：
- 开局：韩立入门派，获得小绿瓶
- 发展：猥琐发育，到处收集资源
- 高潮：越阶战斗，以弱胜强
- 核心节奏：资源积累→境界提升→遇到危机→化解危机

《诡秘之主》结构：
- 开局：穿越到异世界，成为非凡者
- 发展：升级序列，解谜历史
- 高潮：对抗邪神，拯救世界
- 核心节奏：解谜→升级→新的谜团→更大的谜团

【网文结构公式】

第一章（开局章）：
- 建立主角处境
- 抛出核心冲突
- 埋下悬念钩子
- 300字内扔炸弹

第二章（中局章）：
- 金手指出现
- 初步展示潜力
- 埋下更大伏笔

第三章（爆发章）：
- 第一个小高潮
- 解决开局冲突（或部分解决）
- 留下更大悬念

【章节大纲要素】

每个章节大纲需要包含：
1. 章节核心事件
2. 冲突/矛盾
3. 情感转折
4. 悬念/伏笔
5. 爽点设计

请严格按照以上结构设计原则进行大纲规划。"""
    
    def plan_chapter(
        self,
        chapter_num: int,
        volume_num: int,
        guidance: str = "",
        context: Dict = None
    ) -> 'ChapterOutlineResult':
        """规划单章大纲"""
        if not self.llm:
            return self._fallback_plan(chapter_num, volume_num)
        
        context_info = ""
        if context:
            long_term = context.get('long_term', {})
            mid_term = context.get('mid_term', {})
            pending_hooks = context.get('pending_hooks', [])
            
            context_info = f"""
## 当前上下文

"""
            if pending_hooks:
                context_info += f"### 待回收伏笔\n"
                for hook in pending_hooks[:3]:
                    context_info += f"- {hook.get('content', '')}\n"
        
        prompt = f"""请为第{volume_num}卷第{chapter_num}章设计详细大纲：

{context_info}

{f"## 作者指导\n{guidance}\n" if guidance else ""}

请输出JSON格式：
```json
{{
    "title": "章节标题",
    "synopsis": "章节概要（200字）",
    "core_event": "核心事件",
    "conflict": "主要冲突",
    "shuangdian": "爽点设计",
    "hook": "章尾钩子",
    "scenes": [
        {{"location": "地点", "time": "时间", "characters": ["角色"], "goal": "目标", "conflict": "冲突"}}
    ]
}}
```"""
        
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system=self.get_system_prompt(),
                temperature=0.7,
                max_tokens=1500
            )
            
            return self._parse_chapter_plan(response.content, chapter_num, volume_num)
        except Exception as e:
            return self._fallback_plan(chapter_num, volume_num)
    
    def _fallback_plan(self, chapter_num: int, volume_num: int) -> 'ChapterOutlineResult':
        """备用大纲规划"""
        if chapter_num == 1:
            title = "意外的开始"
            synopsis = "主角身处困境，面临重大抉择。一个神秘机缘的出现，打破了平静的生活..."
            shuangdian = "金手指初现"
            hook = "更大的危机即将来临"
        elif chapter_num == 2:
            title = "初露锋芒"
            synopsis = "主角开始探索自己的能力，在小试牛刀中获得信心..."
            shuangdian = "小试牛刀成功"
            hook = "更强的敌人出现"
        elif chapter_num == 3:
            title = "危机降临"
            synopsis = "敌人来袭，主角陷入绝境，但也是展现潜力的时刻..."
            shuangdian = "绝境逆袭"
            hook = "神秘势力介入"
        else:
            title = f"第{chapter_num}章"
            synopsis = "剧情继续推进，主角在挑战中成长..."
            shuangdian = "稳扎稳打"
            hook = "新的机遇出现"
        
        return ChapterOutlineResult(
            title=title,
            synopsis=synopsis,
            core_event="情节推进",
            conflict="困难与挑战",
            shuangdian=shuangdian,
            hook=hook,
            scenes=[]
        )
    
    def _parse_chapter_plan(
        self,
        response: str,
        chapter_num: int,
        volume_num: int
    ) -> 'ChapterOutlineResult':
        """解析章节规划响应"""
        import json
        import re
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return ChapterOutlineResult(
                    title=data.get('title', f'第{chapter_num}章'),
                    synopsis=data.get('synopsis', ''),
                    core_event=data.get('core_event', ''),
                    conflict=data.get('conflict', ''),
                    shuangdian=data.get('shuangdian', ''),
                    hook=data.get('hook', ''),
                    scenes=data.get('scenes', [])
                )
            except json.JSONDecodeError:
                pass
        
        return ChapterOutlineResult(
            title=f'第{chapter_num}章',
            synopsis=response[:500] if response else '',
            core_event='',
            conflict='',
            shuangdian='',
            hook='',
            scenes=[]
        )
    
    def design_volume_outline(
        self,
        volume_num: int,
        chapter_count: int,
        genre: str
    ) -> List[Dict[str, str]]:
        """设计单卷章节大纲"""
        outlines = []
        for i in range(chapter_count):
            ch_num = i + 1
            outline = self.plan_chapter(ch_num, volume_num)
            outlines.append({
                "chapter_num": ch_num,
                "title": outline.title,
                "synopsis": outline.synopsis
            })
        return outlines


@dataclass
class ChapterOutlineResult:
    """章节大纲结果"""
    title: str
    synopsis: str = ""
    core_event: str = ""
    conflict: str = ""
    shuangdian: str = ""
    hook: str = ""
    scenes: List[Dict] = None
    
    def __post_init__(self):
        if self.scenes is None:
            self.scenes = []
