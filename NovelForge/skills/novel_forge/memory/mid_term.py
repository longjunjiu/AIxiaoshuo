"""
中期记忆系统 - 管理当前卷的记忆
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ChapterSummary:
    """章节摘要"""
    number: int
    title: str
    characters_present: List[str] = field(default_factory=list)
    key_events: List[str] = field(default_factory=list)
    state_changes: List[str] = field(default_factory=list)
    hooks_planted: List[str] = field(default_factory=list)
    hooks_recycled: List[str] = field(default_factory=list)
    emotional_moments: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        lines = [
            f"## 第{self.number}章：{self.title}",
            "",
            "### 出场角色",
            ", ".join(self.characters_present) if self.characters_present else "无",
            "",
            "### 关键事件",
        ]
        for event in self.key_events:
            lines.append(f"- {event}")
        
        if self.state_changes:
            lines.extend(["", "### 状态变化"])
            for change in self.state_changes:
                lines.append(f"- {change}")
        
        if self.hooks_planted:
            lines.extend(["", "### 植入伏笔"])
            for hook in self.hooks_planted:
                lines.append(f"- {hook}")
        
        if self.hooks_recycled:
            lines.extend(["", "### 回收伏笔"])
            for hook in self.hooks_recycled:
                lines.append(f"- {hook}")
        
        return "\n".join(lines)


@dataclass
class Subplot:
    """支线"""
    id: str
    name: str
    status: str = "active"  # active, resolved, abandoned
    progress: float = 0.0  # 0-1
    key_milestones: List[str] = field(default_factory=list)
    current_stage: str = ""


@dataclass
class EmotionalArc:
    """情感弧线"""
    character: str
    arc_type: str = "neutral"  # growth, decline, transformation, flat
    stages: List[Dict[str, str]] = field(default_factory=list)
    current_emotion: str = "neutral"
    emotional_range: List[str] = field(default_factory=list)


class MidTermMemory:
    """
    中期记忆管理器
    
    管理当前卷的章节摘要、支线追踪、情感弧线等
    """
    
    def __init__(self, project, volume_num: int = 1):
        self.project = project
        self.volume_num = volume_num
        self.summaries: Dict[int, ChapterSummary] = {}
        self.subplots: Dict[str, Subplot] = {}
        self.emotional_arcs: Dict[str, EmotionalArc] = {}
        
        self._load_from_volume()
    
    def _get_memory_path(self) -> Path:
        """获取记忆文件路径"""
        return self.project.project_path / f"volumes/volume_{self.volume_num}/memory"
    
    def _load_from_volume(self):
        """从卷目录加载记忆"""
        memory_path = self._get_memory_path()
        memory_path.mkdir(parents=True, exist_ok=True)
        
        summaries_path = memory_path / "summaries.md"
        if summaries_path.exists():
            self._parse_summaries(summaries_path)
        
        subplot_path = memory_path / "subplot_board.md"
        if subplot_path.exists():
            self._parse_subplots(subplot_path)
        
        emotional_path = memory_path / "emotional_arcs.md"
        if emotional_path.exists():
            self._parse_emotional_arcs(emotional_path)
    
    def _parse_summaries(self, path: Path):
        """解析章节摘要"""
        content = path.read_text(encoding='utf-8')
        current_chapter = None
        current_data = {}
        
        for line in content.split('\n'):
            if line.startswith('## 第') and '章' in line:
                if current_chapter and current_data:
                    self.summaries[current_chapter] = ChapterSummary(
                        number=current_chapter,
                        title=current_data.get('title', ''),
                        characters_present=current_data.get('characters', []),
                        key_events=current_data.get('events', []),
                        state_changes=current_data.get('changes', []),
                        hooks_planted=current_data.get('hooks_planted', []),
                        hooks_recycled=current_data.get('hooks_recycled', [])
                    )
                
                import re
                match = re.match(r'## 第(\d+)章[：:](.+)', line)
                if match:
                    current_chapter = int(match.group(1))
                    current_data = {'title': match.group(2).strip()}
                else:
                    current_chapter = None
                    current_data = {}
            
            elif current_chapter and line.strip().startswith('-'):
                content_item = line.strip()[1:].strip()
                if '### 出场角色' not in line:
                    if '### 关键事件' in line:
                        current_data.setdefault('events', []).append(content_item)
                    elif '状态变化' in line:
                        current_data.setdefault('changes', []).append(content_item)
                    elif '植入伏笔' in line:
                        current_data.setdefault('hooks_planted', []).append(content_item)
                    elif '回收伏笔' in line:
                        current_data.setdefault('hooks_recycled', []).append(content_item)
    
    def _parse_subplots(self, path: Path):
        """解析支线追踪板"""
        for line in path.read_text(encoding="utf-8").split("\n"):
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5 and parts[1] and parts[1] not in ("支线ID", "-", ""):
                sp_id = parts[1]
                try:
                    progress = float(parts[4].rstrip("%")) / 100 if parts[4].rstrip("%").replace(".", "").isdigit() else 0.0
                except (ValueError, IndexError):
                    progress = 0.0
                self.subplots[sp_id] = Subplot(
                    id=sp_id,
                    name=parts[2] if len(parts) > 2 else "",
                    status=parts[3] if len(parts) > 3 else "active",
                    progress=progress,
                    current_stage=parts[5] if len(parts) > 5 else ""
                )

    def _parse_emotional_arcs(self, path: Path):
        """解析情感弧线"""
        import re
        content = path.read_text(encoding="utf-8")
        current_char: Optional[str] = None
        current_arc: Optional[EmotionalArc] = None

        for line in content.split("\n"):
            stripped = line.strip()
            if stripped.startswith("## ") and len(stripped) > 3:
                if current_char and current_arc:
                    self.emotional_arcs[current_char] = current_arc
                current_char = stripped[3:].strip()
                current_arc = EmotionalArc(character=current_char)
            elif current_arc:
                if stripped.startswith("- 类型:"):
                    current_arc.arc_type = stripped.split(":", 1)[1].strip()
                elif stripped.startswith("- 当前情绪:"):
                    current_arc.current_emotion = stripped.split(":", 1)[1].strip()
                elif stripped.startswith("- 情绪范围:"):
                    emotions = stripped.split(":", 1)[1].strip()
                    current_arc.emotional_range = [e.strip() for e in emotions.split(",") if e.strip()]
                else:
                    m = re.match(r"- 第(\d+)章[:：]\s*(.+)", stripped)
                    if m:
                        current_arc.stages.append({"chapter": int(m.group(1)), "emotion": m.group(2).strip()})

        if current_char and current_arc:
            self.emotional_arcs[current_char] = current_arc
    
    def save(self):
        """保存记忆"""
        memory_path = self._get_memory_path()
        memory_path.mkdir(parents=True, exist_ok=True)
        
        self._save_summaries(memory_path / "summaries.md")
        self._save_subplots(memory_path / "subplot_board.md")
        self._save_emotional_arcs(memory_path / "emotional_arcs.md")
    
    def _save_summaries(self, path: Path):
        """保存章节摘要"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# 章节摘要\n\n")
            
            for ch_num in sorted(self.summaries.keys()):
                f.write(self.summaries[ch_num].to_markdown())
                f.write("\n\n---\n\n")
    
    def _save_subplots(self, path: Path):
        """保存支线追踪板"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# 支线追踪板\n\n")
            f.write("| 支线ID | 名称 | 状态 | 进度 | 当前阶段 |\n")
            f.write("|--------|------|------|------|----------|\n")
            
            for sp in self.subplots.values():
                f.write(f"| {sp.id} | {sp.name} | {sp.status} | {sp.progress:.0%} | {sp.current_stage} |\n")
    
    def _save_emotional_arcs(self, path: Path):
        """保存情感弧线"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# 情感弧线\n\n")
            
            for char, arc in self.emotional_arcs.items():
                f.write(f"## {char}\n")
                f.write(f"- 类型: {arc.arc_type}\n")
                f.write(f"- 当前情绪: {arc.current_emotion}\n")
                f.write(f"- 情绪范围: {', '.join(arc.emotional_range)}\n")
                
                if arc.stages:
                    f.write("\n### 阶段\n")
                    for stage in arc.stages:
                        f.write(f"- 第{stage['chapter']}章: {stage['emotion']}\n")
                f.write("\n")
    
    def add_summary(
        self,
        chapter_num: int,
        title: str,
        characters: List[str],
        events: List[str],
        state_changes: Optional[List[str]] = None,
        hooks_planted: Optional[List[str]] = None,
        hooks_recycled: Optional[List[str]] = None
    ):
        """添加章节摘要"""
        self.summaries[chapter_num] = ChapterSummary(
            number=chapter_num,
            title=title,
            characters_present=characters,
            key_events=events,
            state_changes=state_changes or [],
            hooks_planted=hooks_planted or [],
            hooks_recycled=hooks_recycled or []
        )
        self.save()
    
    def update_subplot(
        self,
        subplot_id: str,
        name: str = "",
        status: str = "",
        progress: float = -1,
        current_stage: str = ""
    ):
        """更新支线状态"""
        if subplot_id not in self.subplots:
            self.subplots[subplot_id] = Subplot(id=subplot_id, name=name)
        
        sp = self.subplots[subplot_id]
        if name:
            sp.name = name
        if status:
            sp.status = status
        if progress >= 0:
            sp.progress = progress
        if current_stage:
            sp.current_stage = current_stage
        
        self.save()
    
    def update_emotional_arc(
        self,
        character: str,
        chapter: int,
        emotion: str
    ):
        """更新情感弧线"""
        if character not in self.emotional_arcs:
            self.emotional_arcs[character] = EmotionalArc(character=character)
        
        arc = self.emotional_arcs[character]
        arc.current_emotion = emotion
        
        if emotion not in arc.emotional_range:
            arc.emotional_range.append(emotion)
        
        arc.stages.append({
            "chapter": chapter,
            "emotion": emotion
        })
        
        self.save()
    
    def get_volume_summary(self) -> str:
        """获取当前卷摘要"""
        lines = [f"# 第{self.volume_num}卷记忆摘要\n"]
        
        if self.summaries:
            lines.append(f"\n共{len(self.summaries)}章摘要")
            
            recent = list(self.summaries.values())[-3:]
            lines.append("\n## 最近章节")
            for summary in recent:
                lines.append(f"\n### 第{summary.number}章：{summary.title}")
                lines.append(f"事件: {'; '.join(summary.key_events[:3])}")
        
        active_subplots = [s for s in self.subplots.values() if s.status == "active"]
        if active_subplots:
            lines.append("\n## 进行中支线")
            for sp in active_subplots:
                lines.append(f"- {sp.name}: {sp.current_stage} ({sp.progress:.0%})")
        
        return "\n".join(lines)
    
    def get_chapter_context(self, chapter_num: int) -> Dict[str, Any]:
        """获取章节写作上下文"""
        prev_summaries = [
            s for num, s in self.summaries.items()
            if num < chapter_num
        ][-3:]
        
        return {
            "previous_summaries": prev_summaries,
            "volume_summary": self.get_volume_summary(),
            "active_subplots": [s for s in self.subplots.values() if s.status == "active"],
            "character_emotions": {
                char: arc.current_emotion 
                for char, arc in self.emotional_arcs.items()
            }
        }
