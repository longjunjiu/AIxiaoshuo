"""
短期记忆系统 - 管理当前章节的上下文
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class Scene:
    """场景"""
    id: str
    location: str
    time: str  # 时间点或时间段
    characters: List[str] = field(default_factory=list)
    goal: str = ""  # 场景目标
    conflict: str = ""  # 冲突/障碍
    outcome: str = ""  # 场景结果
    content: str = ""  # 场景内容


@dataclass
class ChapterOutline:
    """章节大纲"""
    chapter_num: int
    title: str
    synopsis: str
    scenes: List[Scene] = field(default_factory=list)
    hooks_to_plant: List[str] = field(default_factory=list)
    hooks_to_recycle: List[str] = field(default_factory=list)
    resources_to_change: List[Dict[str, str]] = field(default_factory=list)
    
    def to_prompt(self) -> str:
        lines = [
            f"# 第{self.chapter_num}章：{self.title}",
            "",
            f"## 章节概要",
            self.synopsis,
            "",
            "## 场景结构"
        ]
        
        for i, scene in enumerate(self.scenes, 1):
            lines.append(f"\n### 场景{i}: {scene.location} - {scene.time}")
            lines.append(f"- 角色: {', '.join(scene.characters)}")
            lines.append(f"- 目标: {scene.goal}")
            lines.append(f"- 冲突: {scene.conflict}")
        
        if self.hooks_to_plant:
            lines.extend(["", "## 需要植入的伏笔"])
            for hook in self.hooks_to_plant:
                lines.append(f"- {hook}")
        
        if self.hooks_to_recycle:
            lines.extend(["", "## 需要回收的伏笔"])
            for hook in self.hooks_to_recycle:
                lines.append(f"- {hook}")
        
        if self.resources_to_change:
            lines.extend(["", "## 资源变动"])
            for res in self.resources_to_change:
                lines.append(f"- {res['resource']}: {res['change']}")
        
        return "\n".join(lines)


@dataclass
class WritingContext:
    """写作上下文"""
    chapter_num: int
    volume_num: int
    outline: ChapterOutline
    long_term_context: Dict[str, str]
    mid_term_context: Dict[str, Any]
    
    current_resources: Dict[str, Any] = field(default_factory=dict)
    pending_hooks: List[Dict[str, str]] = field(default_factory=list)
    character_states: Dict[str, str] = field(default_factory=dict)
    
    def to_writer_prompt(self) -> str:
        lines = [
            "# 写作上下文",
            "",
            f"## 当前章节",
            f"卷{self.volume_num} 第{self.chapter_num}章：{self.outline.title}",
            "",
            "## 章节大纲",
            self.outline.synopsis,
            ""
        ]
        
        lines.extend(["", "## 场景"])
        for i, scene in enumerate(self.outline.scenes, 1):
            lines.append(f"\n### 场景{i}: {scene.location} | {scene.time}")
            lines.append(f"角色: {', '.join(scene.characters)}")
            lines.append(f"目标: {scene.goal}")
            lines.append(f"冲突: {scene.conflict}")
            if scene.outcome:
                lines.append(f"结果: {scene.outcome}")
        
        if self.long_term_context:
            lines.extend(["", "## 长期记忆"])
            if self.long_term_context.get('relevant_facts'):
                lines.append("\n### 关键事实")
                lines.append(self.long_term_context['relevant_facts'])
            if self.long_term_context.get('pending_hooks'):
                lines.append("\n### 伏笔追踪")
                lines.append(self.long_term_context['pending_hooks'])
        
        if self.character_states:
            lines.extend(["", "## 角色状态"])
            for char, state in self.character_states.items():
                lines.append(f"- **{char}**: {state}")
        
        if self.pending_hooks:
            lines.extend(["", "## 本章需回收伏笔"])
            for hook in self.pending_hooks:
                lines.append(f"- [{hook['id']}] {hook['content']}")
        
        if self.outline.hooks_to_plant:
            lines.extend(["", "## 本章需植入伏笔"])
            for hook in self.outline.hooks_to_plant:
                lines.append(f"- {hook}")
        
        if self.outline.resources_to_change:
            lines.extend(["", "## 资源变动"])
            for res in self.outline.resources_to_change:
                lines.append(f"- {res['resource']}: {res['change']}")
        
        return "\n".join(lines)


class ShortTermMemory:
    """
    短期记忆管理器
    
    管理当前章节的大纲、场景、上下文等
    """
    
    def __init__(self):
        self.outline: Optional[ChapterOutline] = None
        self.context: Optional[WritingContext] = None
        self.draft: str = ""
        self.revisions: List[str] = []
        self.self_check: Optional[Dict[str, Any]] = None
    
    def set_outline(self, outline: ChapterOutline):
        """设置章节大纲"""
        self.outline = outline
    
    def set_context(self, context: WritingContext):
        """设置写作上下文"""
        self.context = context
    
    def set_draft(self, draft: str):
        """设置草稿"""
        if not self.draft:
            self.draft = draft
        else:
            self.revisions.append(self.draft)
            self.draft = draft
    
    def get_previous_revision(self) -> Optional[str]:
        """获取上一版本草稿"""
        if self.revisions:
            return self.revisions[-1]
        return None
    
    def set_self_check(self, check_result: Dict[str, Any]):
        """设置自检结果"""
        self.self_check = check_result
    
    def generate_pre_write_checklist(self) -> str:
        """生成写前自检清单"""
        if not self.context or not self.outline:
            return ""
        
        lines = [
            "# 写前自检清单",
            "",
            "请在动笔前确认以下事项：",
            "",
            "## 上下文范围",
            f"- 当前章节: 第{self.context.chapter_num}章",
            f"- 当前卷: 第{self.context.volume_num}卷",
            f"- 章节标题: {self.outline.title}",
            "",
            "## 当前资源状态",
        ]
        
        if self.context.current_resources:
            for res, amount in self.context.current_resources.items():
                lines.append(f"- {res}: {amount}")
        else:
            lines.append("- 暂无资源追踪")
        
        lines.extend([
            "",
            "## 待回收伏笔",
        ])
        
        if self.context.pending_hooks:
            for hook in self.context.pending_hooks:
                lines.append(f"- [{hook['id']}] {hook['content']}")
        else:
            lines.append("- 无待回收伏笔")
        
        lines.extend([
            "",
            "## 冲突概述",
            "- 确认角色间关系正确",
            "- 确认时间线连贯",
            "- 确认信息边界（角色只知其应知之事）",
            "",
            "## 风险扫描",
            "- 本章是否涉及重要设定变更？",
            "- 本章是否有角色死亡/离开/加入？",
            "- 本章是否有伏笔植入/回收？",
            "",
            "请确认以上信息后再开始写作。"
        ])
        
        return "\n".join(lines)
    
    def generate_post_write_settlement(self) -> str:
        """生成写后结算清单"""
        if not self.outline:
            return ""
        
        lines = [
            "# 写后结算清单",
            "",
            "请在完成写作后填写以下信息：",
            "",
            "## 资源变动",
            "- 请列出本章中发生的所有资源变动",
            "- 格式: 资源名 | 变动(+/-数量) | 原因",
            "",
            "## 伏笔变动",
        ]
        
        if self.outline.hooks_to_plant:
            lines.append("\n### 植入伏笔")
            for hook in self.outline.hooks_to_plant:
                lines.append(f"- {hook}")
        
        if self.outline.hooks_to_recycle:
            lines.append("\n### 回收伏笔")
            for hook in self.outline.hooks_to_recycle:
                lines.append(f"- {hook}")
        
        lines.extend([
            "",
            "## 角色状态变化",
            "- 列出本章中发生的所有角色状态变化",
            "",
            "## 信息揭露",
            "- 本章揭露了哪些新信息？",
            "- 这些信息哪些角色应该知道？",
            "- 是否有信息越界（角色知道了不该知道的）？",
        ])
        
        return "\n".join(lines)
    
    def clear(self):
        """清空短期记忆"""
        self.outline = None
        self.context = None
        self.draft = ""
        self.revisions = []
        self.self_check = None
