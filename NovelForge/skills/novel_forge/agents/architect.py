"""
建筑师Agent - 规划章节结构和大纲
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..memory.short_term import ChapterOutline, Scene
from ..rules.craft import CraftRules


@dataclass
class BeatPlan:
    """节拍计划"""
    beat_name: str
    position: float
    description: str
    characters: List[str]
    location: str
    time: str


class ArchitectAgent:
    """
    建筑师Agent
    
    负责规划章节结构，包括：
    - 场景划分
    - 节拍安排
    - 伏笔植入点
    - 资源变动点
    """
    
    def __init__(self, llm_client, project, craft_rules: Optional[CraftRules] = None):
        self.llm = llm_client
        self.project = project
        self.craft = craft_rules or CraftRules()
    
    def plan_chapter(
        self,
        chapter_num: int,
        volume_num: int = 1,
        guidance: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> ChapterOutline:
        """
        规划章节大纲
        
        Args:
            chapter_num: 章节号
            volume_num: 卷号
            guidance: 章节指导
            context: 上下文信息
            
        Returns:
            章节大纲
        """
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_planning_prompt(chapter_num, volume_num, guidance, context)
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.7,
            max_tokens=3000
        )
        
        return self._parse_outline(response.content, chapter_num)
    
    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return f"""你是一位专业的小说建筑师，负责规划章节结构。

你的职责：
1. 根据故事整体大纲，将章节分解为具体的场景
2. 为每个场景设定明确的目标、冲突和角色
3. 规划伏笔的植入和回收时机
4. 确保节奏起伏适当
5. 与全书记忆保持一致

创作规则：
{self.craft.get_all_rules_prompt()}

输出格式必须符合JSON结构，包含以下字段：
- title: 章节标题
- synopsis: 章节概要（100字内）
- scenes: 场景列表，每场景包含location, time, characters, goal, conflict
- hooks_to_plant: 需植入的伏笔列表
- hooks_to_recycle: 需回收的伏笔列表
- resources_to_change: 资源变动列表

请直接输出JSON，不要有其他内容。"""
    
    def _build_planning_prompt(
        self,
        chapter_num: int,
        volume_num: int,
        guidance: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """构建规划提示"""
        lines = [
            f"# 章节规划任务",
            "",
            f"章节号: 第{chapter_num}章",
            f"卷号: 第{volume_num}卷",
            f"目标字数: {self.project.target_words_per_chapter}字",
            ""
        ]
        
        if guidance:
            lines.extend([
                "## 章节指导",
                guidance,
                ""
            ])
        
        if context:
            if context.get('previous_summary'):
                lines.extend([
                    "## 前章摘要",
                    context['previous_summary'],
                    ""
                ])
            
            if context.get('outline'):
                lines.extend([
                    "## 章节大纲",
                    context['outline'],
                    ""
                ])
            
            if context.get('pending_hooks'):
                lines.extend([
                    "## 待回收伏笔",
                    context['pending_hooks'],
                    ""
                ])
        
        lines.extend([
            "## 创作要求",
            f"1. 将本章分解为3-5个场景",
            "2. 每个场景明确：地点、时间、角色、目标、冲突",
            "3. 标注需要植入和回收的伏笔",
            "4. 规划资源变动（如有）",
            "5. 确保场景间有过渡，节奏有起伏"
        ])
        
        return "\n".join(lines)
    
    def _parse_outline(self, response: str, chapter_num: int) -> ChapterOutline:
        """解析大纲响应"""
        import json
        import re
        
        json_match = re.search(r'\{[\s\S]*\}', response)
        if not json_match:
            return ChapterOutline(
                chapter_num=chapter_num,
                title=f"第{chapter_num}章",
                synopsis="",
                scenes=[]
            )
        
        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError:
            return ChapterOutline(
                chapter_num=chapter_num,
                title=f"第{chapter_num}章",
                synopsis="",
                scenes=[]
            )
        
        scenes = []
        for s in data.get('scenes', []):
            scene = Scene(
                id=f"scene_{len(scenes) + 1}",
                location=s.get('location', ''),
                time=s.get('time', ''),
                characters=s.get('characters', []),
                goal=s.get('goal', ''),
                conflict=s.get('conflict', ''),
                outcome=s.get('outcome', '')
            )
            scenes.append(scene)
        
        return ChapterOutline(
            chapter_num=chapter_num,
            title=data.get('title', f'第{chapter_num}章'),
            synopsis=data.get('synopsis', ''),
            scenes=scenes,
            hooks_to_plant=data.get('hooks_to_plant', []),
            hooks_to_recycle=data.get('hooks_to_recycle', []),
            resources_to_change=data.get('resources_to_change', [])
        )
    
    def plan_volume(
        self,
        volume_num: int,
        start_chapter: int,
        end_chapter: int,
        volume_synopsis: str = ""
    ) -> List[ChapterOutline]:
        """
        规划整卷章节
        
        Args:
            volume_num: 卷号
            start_chapter: 起始章节
            end_chapter: 结束章节
            volume_synopsis: 卷概要
            
        Returns:
            章节大纲列表
        """
        outlines = []
        
        for ch in range(start_chapter, end_chapter + 1):
            outline = self.plan_chapter(
                chapter_num=ch,
                volume_num=volume_num,
                guidance=f"这是第{volume_num}卷的章节，卷概要: {volume_synopsis}"
            )
            outlines.append(outline)
        
        return outlines
    
    def refine_outline(
        self,
        outline: ChapterOutline,
        feedback: str
    ) -> ChapterOutline:
        """
        根据反馈精化大纲
        
        Args:
            outline: 当前大纲
            feedback: 反馈意见
            
        Returns:
            精化后的大纲
        """
        system_prompt = """你是一位专业的小说建筑师，根据反馈精化章节大纲。

规则：
1. 只修改必要部分，保留合理内容
2. 确保修改后的逻辑连贯
3. 保持伏笔的一致性

输出格式必须是JSON，包含完整的大纲结构。"""
        
        user_prompt = f"""# 当前大纲
{outline.to_prompt()}

# 反馈意见
{feedback}

请根据反馈修改大纲，直接输出JSON。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.5,
            max_tokens=3000
        )
        
        return self._parse_outline(response.content, outline.chapter_num)
