"""
长期记忆系统 - 管理全书级别的记忆
"""

import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field, asdict


@dataclass
class Hook:
    """伏笔"""
    id: str
    content: str
    plant_chapter: int
    expected_recycle_chapter: Optional[int] = None
    actual_recycle_chapter: Optional[int] = None
    hook_type: str = "plot"  # plot, character, world
    status: str = "pending"  # pending, recycled, abandoned
    quality: str = ""  # subtle, obvious, heavy
    evaluation: str = ""
    
    def mark_recycled(self, chapter: int, evaluation: str = ""):
        self.actual_recycle_chapter = chapter
        self.status = "recycled"
        self.evaluation = evaluation


@dataclass
class CanonFact:
    """硬性事实"""
    fact: str
    source_chapter: int
    category: str = "general"  # world, character, plot, timeline
    verified: bool = False


@dataclass
class CharacterState:
    """角色状态"""
    name: str
    location: str = "unknown"
    relationships: Dict[str, str] = field(default_factory=dict)
    knowledge: List[str] = field(default_factory=list)
    emotional_state: str = "neutral"
    physical_state: str = "healthy"
    resources: Dict[str, Any] = field(default_factory=dict)
    last_update_chapter: int = 0


@dataclass
class ResourceChange:
    """资源变动"""
    resource: str
    change: str  # +100, -50, lost, gained
    chapter: int
    reason: str = ""


class LongTermMemory:
    """
    长期记忆管理器
    
    维护全书级别的真相文件、伏笔网络、资源账本等
    """
    
    def __init__(self, project):
        self.project = project
        self.hooks: Dict[str, Hook] = {}
        self.canon_facts: List[CanonFact] = []
        self.character_states: Dict[str, CharacterState] = {}
        self.resource_changes: List[ResourceChange] = []
        
        self._load_from_project()
    
    def _load_from_project(self):
        """从项目加载记忆"""
        memory_path = self.project.project_path / "memory"
        
        if not memory_path.exists():
            memory_path.mkdir(parents=True, exist_ok=True)
            return
        
        canon_path = memory_path / "canon.md"
        if canon_path.exists():
            self._parse_canon(canon_path)
        
        hooks_path = memory_path / "hook_network.md"
        if hooks_path.exists():
            self._parse_hooks(hooks_path)
    
    def _parse_canon(self, path: Path):
        """解析真相文件"""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        fact_pattern = re.compile(r'-\s*(.+?)\s*-\s*第(\d+)章', re.UNICODE)
        for match in fact_pattern.finditer(content):
            self.canon_facts.append(CanonFact(
                fact=match.group(1),
                source_chapter=int(match.group(2))
            ))
    
    def _parse_hooks(self, path: Path):
        """解析伏笔网络"""
        pending_section = False
        for line in path.read_text(encoding='utf-8').split('\n'):
            if '待回收伏笔' in line:
                pending_section = True
                continue
            if '已回收伏笔' in line:
                pending_section = False
                continue
            
            if '|' in line and pending_section:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 5 and parts[0] != '-':
                    hook = Hook(
                        id=parts[0],
                        content=parts[1],
                        plant_chapter=int(parts[2]) if parts[2].isdigit() else 0,
                        expected_recycle_chapter=int(parts[3]) if parts[3].isdigit() else None,
                        status="pending" if "待" in parts[4] else parts[4]
                    )
                    self.hooks[hook.id] = hook
    
    def save(self):
        """保存记忆到项目"""
        memory_path = self.project.project_path / "memory"
        memory_path.mkdir(parents=True, exist_ok=True)
        
        self._save_canon(memory_path / "canon.md")
        self._save_hooks(memory_path / "hook_network.md")
        self._save_resource_ledger(memory_path / "resource_ledger.md")
    
    def _save_canon(self, path: Path):
        """保存真相文件"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# 真相文件\n\n本文档记录小说中所有硬性事实，供审计使用。\n\n")
            f.write("格式：[事实] - [来源章节]\n\n")
            
            for fact in self.canon_facts:
                f.write(f"- {fact.fact} - 第{fact.source_chapter}章\n")
    
    def _save_hooks(self, path: Path):
        """保存伏笔网络"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# 伏笔网络\n\n")
            f.write("## 待回收伏笔\n\n")
            f.write("| 伏笔ID | 内容 | 植入章节 | 预期回收 | 状态 |\n")
            f.write("|--------|------|----------|----------|------|\n")
            
            for hook in self.hooks.values():
                if hook.status == "pending":
                    f.write(f"| {hook.id} | {hook.content} | {hook.plant_chapter} | ")
                    f.write(f"{hook.expected_recycle_chapter or '-'} | 待回收 |\n")
            
            f.write("\n## 已回收伏笔\n\n")
            f.write("| 伏笔ID | 内容 | 回收章节 | 评价 |\n")
            f.write("|--------|------|----------|------|\n")
            
            for hook in self.hooks.values():
                if hook.status == "recycled":
                    f.write(f"| {hook.id} | {hook.content} | {hook.actual_recycle_chapter} | ")
                    f.write(f"{hook.evaluation or '-'} |\n")
    
    def _save_resource_ledger(self, path: Path):
        """保存资源账本"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# 资源账本\n\n")
            f.write("## 资源变动记录\n\n")
            f.write("| 资源 | 变动 | 章节 | 原因 |\n")
            f.write("|------|------|------|------|\n")
            
            for change in self.resource_changes[-50:]:
                f.write(f"| {change.resource} | {change.change} | {change.chapter} | {change.reason} |\n")
    
    def add_hook(
        self,
        content: str,
        plant_chapter: int,
        hook_type: str = "plot",
        expected_recycle: Optional[int] = None
    ) -> str:
        """
        添加伏笔
        
        Args:
            content: 伏笔内容
            plant_chapter: 植入章节
            hook_type: 伏笔类型
            expected_recycle: 预期回收章节
            
        Returns:
            伏笔ID
        """
        hook_id = f"hook_{len(self.hooks) + 1:04d}"
        
        hook = Hook(
            id=hook_id,
            content=content,
            plant_chapter=plant_chapter,
            expected_recycle_chapter=expected_recycle,
            hook_type=hook_type
        )
        
        self.hooks[hook_id] = hook
        self.save()
        
        return hook_id
    
    def recycle_hook(
        self,
        hook_id: str,
        recycle_chapter: int,
        evaluation: str = ""
    ):
        """
        回收伏笔
        
        Args:
            hook_id: 伏笔ID
            recycle_chapter: 回收章节
            evaluation: 评价
        """
        if hook_id in self.hooks:
            self.hooks[hook_id].mark_recycled(recycle_chapter, evaluation)
            self.save()
    
    def add_canon_fact(
        self,
        fact: str,
        source_chapter: int,
        category: str = "general"
    ):
        """添加硬性事实"""
        canon = CanonFact(
            fact=fact,
            source_chapter=source_chapter,
            category=category
        )
        self.canon_facts.append(canon)
        self.save()
    
    def update_character_state(
        self,
        name: str,
        location: Optional[str] = None,
        relationship: Optional[tuple] = None,
        knowledge: Optional[str] = None,
        emotional_state: Optional[str] = None,
        physical_state: Optional[str] = None,
        chapter: int = 0
    ):
        """更新角色状态"""
        if name not in self.character_states:
            self.character_states[name] = CharacterState(name=name)
        
        state = self.character_states[name]
        state.last_update_chapter = chapter
        
        if location:
            state.location = location
        if relationship:
            state.relationships[relationship[0]] = relationship[1]
        if knowledge:
            if knowledge not in state.knowledge:
                state.knowledge.append(knowledge)
        if emotional_state:
            state.emotional_state = emotional_state
        if physical_state:
            state.physical_state = physical_state
    
    def add_resource_change(
        self,
        resource: str,
        change: str,
        chapter: int,
        reason: str = ""
    ):
        """添加资源变动"""
        self.resource_changes.append(ResourceChange(
            resource=resource,
            change=change,
            chapter=chapter,
            reason=reason
        ))
    
    def get_context_for_chapter(
        self,
        chapter_num: int,
        volume_num: int = 1
    ) -> Dict[str, str]:
        """
        获取写作章节所需的上下文记忆
        
        Args:
            chapter_num: 章节号
            volume_num: 卷号
            
        Returns:
            上下文字典
        """
        context = {
            "relevant_facts": self._get_relevant_facts(chapter_num),
            "pending_hooks": self._get_pending_hooks(chapter_num),
            "character_states": self._get_character_summary(),
            "recent_resource_changes": self._get_recent_resources(chapter_num),
            "previous_chapter_summary": self._get_previous_summary(chapter_num)
        }
        
        return context
    
    def _get_relevant_facts(self, chapter_num: int, limit: int = 20) -> str:
        """获取相关事实"""
        recent_facts = [
            f for f in self.canon_facts
            if f.source_chapter < chapter_num
        ][-limit:]
        
        return "\n".join([
            f"- {fact.fact} (第{fact.source_chapter}章)"
            for fact in recent_facts
        ])
    
    def _get_pending_hooks(self, chapter_num: int) -> str:
        """获取待回收伏笔"""
        pending = [
            h for h in self.hooks.values()
            if h.status == "pending"
        ]
        
        imminent = [h for h in pending if h.expected_recycle_chapter and h.expected_recycle_chapter <= chapter_num + 5]
        
        lines = ["## 伏笔追踪\n"]
        
        if imminent:
            lines.append("### 即将到期\n")
            for h in imminent:
                lines.append(f"- **[应回收]** {h.content} (植入于第{h.plant_chapter}章)")
        
        if pending:
            lines.append("\n### 全部待回收\n")
            for h in pending[:10]:
                lines.append(f"- {h.content} (植入于第{h.plant_chapter}章)")
        
        return "\n".join(lines)
    
    def _get_character_summary(self) -> str:
        """获取角色状态摘要"""
        lines = ["## 角色状态\n"]
        
        for name, state in self.character_states.items():
            lines.append(f"\n### {name}\n")
            lines.append(f"- 位置: {state.location}")
            lines.append(f"- 情绪: {state.emotional_state}")
            lines.append(f"- 状态: {state.physical_state}")
            
            if state.relationships:
                lines.append("- 关系:")
                for other, rel in state.relationships.items():
                    lines.append(f"  - {other}: {rel}")
            
            if state.knowledge:
                lines.append(f"- 已知信息: {', '.join(state.knowledge[-3:])}")
        
        return "\n".join(lines)
    
    def _get_recent_resources(self, chapter_num: int, limit: int = 10) -> str:
        """获取最近资源变动"""
        recent = [
            r for r in self.resource_changes
            if r.chapter < chapter_num
        ][-limit:]
        
        lines = ["## 最近资源变动\n"]
        for r in recent:
            lines.append(f"- {r.resource}: {r.change} (第{r.chapter}章)")
        
        return "\n".join(lines) if lines else "## 最近资源变动\n无"
    
    def _get_previous_summary(self, chapter_num: int) -> str:
        """获取前章摘要"""
        if chapter_num <= 1:
            return "## 前章摘要\n这是第一章，无前文。"
        
        summary_path = self.project.project_path / f"volumes/volume_{self.project.current_volume}/memory/summaries.md"
        
        if summary_path.exists():
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            prev_summary = []
            for i, line in enumerate(lines):
                if f'第{chapter_num - 1}章' in line:
                    prev_summary = lines[i:i+10]
                    break
            
            if prev_summary:
                return "## 前章摘要\n" + "\n".join(prev_summary)
        
        return f"## 前章摘要\n第{chapter_num - 1}章已完成，请参考该章内容。"
    
    def get_hook_status(self) -> Dict[str, Any]:
        """获取伏笔状态统计"""
        pending = [h for h in self.hooks.values() if h.status == "pending"]
        recycled = [h for h in self.hooks.values() if h.status == "recycled"]
        
        return {
            "total": len(self.hooks),
            "pending_count": len(pending),
            "recycled_count": len(recycled),
            "recycle_rate": len(recycled) / len(self.hooks) if self.hooks else 0,
            "pending_hooks": [
                {"id": h.id, "content": h.content, "plant_chapter": h.plant_chapter}
                for h in pending[:20]
            ],
            "recently_recycled": [
                {"id": h.id, "content": h.content, "recycle_chapter": h.actual_recycle_chapter}
                for h in recycled[-5:]
            ]
        }
    
    def check_hook_completion(self, chapter_num: int) -> List[Dict[str, Any]]:
        """检查伏笔完成情况"""
        warnings = []
        imminent = [h for h in self.hooks.values() 
                   if h.status == "pending" 
                   and h.expected_recycle_chapter 
                   and h.expected_recycle_chapter == chapter_num]
        
        overdue = [h for h in self.hooks.values() 
                  if h.status == "pending" 
                  and h.expected_recycle_chapter 
                  and h.expected_recycle_chapter < chapter_num]
        
        for h in overdue:
            warnings.append({
                "type": "overdue",
                "hook": h,
                "message": f"伏笔'{h.content}'已逾期未回收（预期第{h.expected_recycle_chapter}章）"
            })
        
        for h in imminent:
            warnings.append({
                "type": "imminent",
                "hook": h,
                "message": f"伏笔'{h.content}'应在本书回收"
            })
        
        return warnings
