"""
NovelManager - 小说项目管理器
负责小说的创建、加载、保存和导出
"""

import os
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Chapter:
    """章节数据"""
    number: int
    title: str
    content: str = ""
    word_count: int = 0
    status: str = "draft"  # draft, revised, final
    created_at: str = ""
    updated_at: str = ""
    hooks_planted: List[str] = field(default_factory=list)
    hooks_recycled: List[str] = field(default_factory=list)
    resources_changed: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


@dataclass
class Volume:
    """卷数据"""
    number: int
    title: str
    synopsis: str = ""
    start_chapter: int = 0
    end_chapter: int = 0
    chapters: Dict[int, Chapter] = field(default_factory=dict)
    
    @property
    def word_count(self) -> int:
        return sum(ch.word_count for ch in self.chapters.values())
    
    @property
    def chapter_count(self) -> int:
        return len(self.chapters)


@dataclass
class NovelProject:
    """小说项目"""
    title: str
    genre: str
    synopsis: str
    target_chapters: int = 1000
    target_words_per_chapter: int = 3000
    created_at: str = ""
    
    volumes: Dict[int, Volume] = field(default_factory=dict)
    chapters: Dict[int, Chapter] = field(default_factory=dict)
    current_volume: int = 1
    total_chapters: int = 0
    
    world_settings: Dict[str, str] = field(default_factory=dict)
    character_profiles: Dict[str, Dict] = field(default_factory=dict)
    system_settings: Dict[str, Any] = field(default_factory=dict)
    
    canon_facts: List[str] = field(default_factory=list)
    hook_network: Dict[str, Dict] = field(default_factory=dict)
    resource_ledger: Dict[str, Any] = field(default_factory=dict)
    style_profile: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def project_path(self) -> Path:
        return self._project_path
    
    @project_path.setter
    def project_path(self, path: Path):
        self._project_path = path
    
    def save(self):
        """保存项目"""
        NovelManager.save_project(self)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        data.pop('_project_path', None)
        return data


class NovelManager:
    """小说项目管理器"""
    
    @staticmethod
    def create_project(
        title: str,
        genre: str,
        synopsis: str,
        target_chapters: int = 1000,
        target_words_per_chapter: int = 3000,
        output_dir: str = "./novels"
    ) -> NovelProject:
        """
        创建新项目
        
        Args:
            title: 书名
            genre: 题材
            synopsis: 简介
            target_chapters: 目标章节数
            target_words_per_chapter: 每章目标字数
            output_dir: 输出目录
            
        Returns:
            NovelProject实例
        """
        project = NovelProject(
            title=title,
            genre=genre,
            synopsis=synopsis,
            target_chapters=target_chapters,
            target_words_per_chapter=target_words_per_chapter,
            created_at=datetime.now().isoformat()
        )
        
        safe_title = NovelManager._sanitize_title(title)
        project_path = Path(output_dir) / safe_title
        project.project_path = project_path
        
        NovelManager._create_directory_structure(project_path)
        NovelManager._create_initial_files(project_path, project)
        
        return project
    
    @staticmethod
    def load_project(project_path: str) -> NovelProject:
        """
        加载现有项目
        
        Args:
            project_path: 项目路径
            
        Returns:
            NovelProject实例
        """
        project_path = Path(project_path)
        
        config_path = project_path / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        project = NovelProject(
            title=config['title'],
            genre=config['genre'],
            synopsis=config.get('synopsis', ''),
            target_chapters=config.get('target_chapters', 1000),
            target_words_per_chapter=config.get('target_words_per_chapter', 3000),
            created_at=config.get('created_at', '')
        )
        project.project_path = project_path
        
        NovelManager._load_settings(project_path, project)
        NovelManager._load_volumes(project_path, project)
        NovelManager._load_chapters(project_path, project)
        NovelManager._load_memory_files(project_path, project)
        
        return project
    
    @staticmethod
    def save_project(project: NovelProject):
        """保存项目"""
        project_path = project.project_path
        
        config = {
            'title': project.title,
            'genre': project.genre,
            'synopsis': project.synopsis,
            'target_chapters': project.target_chapters,
            'target_words_per_chapter': project.target_words_per_chapter,
            'created_at': project.created_at,
            'current_volume': project.current_volume,
            'total_chapters': project.total_chapters
        }
        
        config_path = project_path / "config.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        NovelManager._save_settings(project_path, project)
        NovelManager._save_chapters(project_path, project)
        NovelManager._save_memory_files(project_path, project)
    
    @staticmethod
    def _sanitize_title(title: str) -> str:
        """清理标题"""
        import re
        return re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    
    @staticmethod
    def _create_directory_structure(project_path: Path):
        """创建目录结构"""
        dirs = [
            "settings",
            "volumes/volume_1/chapters",
            "volumes/volume_1/memory",
            "memory",
            "drafts",
            "audits",
            "revisions",
            "exports"
        ]
        
        for d in dirs:
            (project_path / d).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def _create_initial_files(project_path: Path, project: NovelProject):
        """创建初始文件"""
        config = {
            'title': project.title,
            'genre': project.genre,
            'synopsis': project.synopsis,
            'target_chapters': project.target_chapters,
            'target_words_per_chapter': project.target_words_per_chapter,
            'created_at': project.created_at
        }
        
        with open(project_path / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        template_path = project_path / "settings"
        
        templates = {
            "world.md": f"# {project.title} - 世界观设定\n\n## 世界概述\n\n（待填写）\n\n## 地理环境\n\n## 社会结构\n\n## 历史背景\n\n## 势力分布\n",
            "characters.md": f"# {project.title} - 角色设定\n\n## 主要角色\n\n（待填写）\n\n## 配角\n\n## 势力关系\n",
            "system.md": f"# {project.title} - 体系设定\n\n## {project.genre}体系\n\n（待填写）\n",
            "magic.md": f"# {project.title} - 特殊设定\n\n## 特殊能力/法则\n\n（待填写）\n"
        }
        
        for filename, content in templates.items():
            with open(template_path / filename, 'w', encoding='utf-8') as f:
                f.write(content)
        
        memory_path = project_path / "memory"
        memory_files = {
            "canon.md": "# 真相文件\n\n本文档记录小说中所有硬性事实，供审计使用。\n\n格式：[事实] - [来源章节]\n",
            "hook_network.md": "# 伏笔网络\n\n## 待回收伏笔\n\n| 伏笔ID | 内容 | 植入章节 | 预期回收 | 状态 |\n|--------|------|----------|----------|------|\n| - | - | - | - | - |\n\n## 已回收伏笔\n\n| 伏笔ID | 内容 | 回收章节 | 评价 |\n|--------|------|----------|------|\n| - | - | - | - |\n",
            "resource_ledger.md": "# 资源账本\n\n## 主角资源\n\n| 资源名 | 数量 | 变动记录 | 最后更新 |\n|--------|------|----------|----------|\n| - | - | - | - |\n\n## 重要物品\n\n| 物品名 | 所属 | 状态 | 备注 |\n|--------|------|------|------|\n| - | - | - | - |\n"
        }
        
        for filename, content in memory_files.items():
            with open(memory_path / filename, 'w', encoding='utf-8') as f:
                f.write(content)
        
        volume_outline = project_path / "volumes/volume_1/outline.md"
        with open(volume_outline, 'w', encoding='utf-8') as f:
            f.write("# 第一卷大纲\n\n（待生成）\n")
    
    @staticmethod
    def _load_settings(project_path: Path, project: NovelProject):
        """加载设定文件"""
        settings_path = project_path / "settings"
        
        for filename in ["world.md", "characters.md", "system.md", "magic.md"]:
            filepath = settings_path / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    key = filename.replace(".md", "")
                    project.world_settings[key] = f.read()
    
    @staticmethod
    def _load_volumes(project_path: Path, project: NovelProject):
        """加载卷数据"""
        volumes_path = project_path / "volumes"
        
        for vol_dir in sorted(volumes_path.iterdir()):
            if vol_dir.is_dir() and vol_dir.name.startswith("volume_"):
                vol_num = int(vol_dir.name.split("_")[1])
                outline_path = vol_dir / "outline.md"
                
                volume = Volume(
                    number=vol_num,
                    title=f"第{vol_num}卷",
                    synopsis=""
                )
                
                if outline_path.exists():
                    with open(outline_path, 'r', encoding='utf-8') as f:
                        volume.synopsis = f.read()
                
                project.volumes[vol_num] = volume
    
    @staticmethod
    def _load_chapters(project_path: Path, project: NovelProject):
        """加载章节"""
        chapters_dir = project_path / "volumes/volume_1/chapters"
        
        if chapters_dir.exists():
            for ch_file in sorted(chapters_dir.glob("ch_*.md")):
                ch_num = int(ch_file.stem.split("_")[1])
                
                with open(ch_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = content.split('\n')
                title = lines[0].replace('# ', '').strip() if lines else f"第{ch_num}章"
                
                chapter = Chapter(
                    number=ch_num,
                    title=title,
                    content=content,
                    word_count=len(content)
                )
                
                project.chapters[ch_num] = chapter
                project.total_chapters = max(project.total_chapters, ch_num)
    
    @staticmethod
    def _load_memory_files(project_path: Path, project: NovelProject):
        """加载记忆文件"""
        memory_path = project_path / "memory"
        
        memory_files = ["canon.md", "hook_network.md", "resource_ledger.md"]
        
        for filename in memory_files:
            filepath = memory_path / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    setattr(project, filename.replace(".md", "").replace("_", ""), f.read())
    
    @staticmethod
    def _save_settings(project_path: Path, project: NovelProject):
        """保存设定文件"""
        settings_path = project_path / "settings"
        settings_path.mkdir(parents=True, exist_ok=True)
        
        for key, content in project.world_settings.items():
            filepath = settings_path / f"{key}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
    
    @staticmethod
    def _save_chapters(project_path: Path, project: NovelProject):
        """保存章节"""
        for ch_num, chapter in project.chapters.items():
            vol_num = project.current_volume
            ch_dir = project_path / f"volumes/volume_{vol_num}/chapters"
            ch_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = ch_dir / f"ch_{ch_num:03d}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {chapter.title}\n\n{chapter.content}")
    
    @staticmethod
    def _save_memory_files(project_path: Path, project: NovelProject):
        """保存记忆文件"""
        memory_path = project_path / "memory"
        memory_path.mkdir(parents=True, exist_ok=True)
        
        files = {
            "canon.md": getattr(project, 'canon', ''),
            "hook_network.md": getattr(project, 'hooknetwork', ''),
            "resource_ledger.md": getattr(project, 'resourceledger', '')
        }
        
        for filename, content in files.items():
            if content:
                filepath = memory_path / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
    
    @staticmethod
    def export_novel(
        project: NovelProject,
        format: str = "markdown",
        output_path: Optional[str] = None
    ) -> str:
        """
        导出小说
        
        Args:
            project: 项目实例
            format: 导出格式
            output_path: 输出路径
            
        Returns:
            导出文件路径
        """
        if output_path is None:
            output_path = project.project_path / "exports" / f"{project.title}.{format}"
        else:
            output_path = Path(output_path)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "markdown":
            NovelManager._export_markdown(project, output_path)
        elif format == "text":
            NovelManager._export_text(project, output_path)
        elif format == "json":
            NovelManager._export_json(project, output_path)
        
        return str(output_path)
    
    @staticmethod
    def _export_markdown(project: NovelProject, output_path: Path):
        """导出为Markdown"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {project.title}\n\n")
            f.write(f"**{project.genre}**  |  {project.synopsis}\n\n")
            f.write("---\n\n")
            
            for ch_num in sorted(project.chapters.keys()):
                chapter = project.chapters[ch_num]
                f.write(f"\n## {chapter.title}\n\n")
                f.write(chapter.content)
                f.write("\n\n---\n")
    
    @staticmethod
    def _export_text(project: NovelProject, output_path: Path):
        """导出为纯文本"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"{project.title}\n")
            f.write("=" * len(project.title) + "\n\n")
            
            for ch_num in sorted(project.chapters.keys()):
                chapter = project.chapters[ch_num]
                f.write(f"\n{chapter.title}\n")
                f.write("-" * len(chapter.title) + "\n\n")
                f.write(chapter.content)
                f.write("\n\n")
    
    @staticmethod
    def _export_json(project: NovelProject, output_path: Path):
        """导出为JSON"""
        data = {
            "title": project.title,
            "genre": project.genre,
            "synopsis": project.synopsis,
            "chapters": [
                {
                    "number": ch.number,
                    "title": ch.title,
                    "content": ch.content,
                    "word_count": ch.word_count
                }
                for ch in sorted(project.chapters.values(), key=lambda x: x.number)
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
