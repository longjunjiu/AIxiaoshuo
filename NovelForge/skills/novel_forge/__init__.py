"""
NovelForge - AI小说辅助创作技能
百万字级长篇作品创作系统

核心入口模块
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

from .novel_manager import NovelManager, NovelProject
from .agents.orchestrator import OrchestratorAgent
from .memory.long_term import LongTermMemory
from .audit.detector import AIGCDetector
from .rules.craft import CraftRules
from .rules.anti_slop import AntiSlopRules
from .utils.llm_client import LLMClient


@dataclass
class ForgeConfig:
    """NovelForge配置"""
    llm_provider: str = "openai"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    embedding_model: Optional[str] = None
    enable_vector_store: bool = False


class NovelForge:
    """
    NovelForge AI小说辅助创作技能主类
    
    提供完整的长篇小说创作能力：
    - 多Agent协作写作
    - 三层记忆系统
    - 伏笔追踪管理
    - 26维度质量审计
    - AIGC检测与去AI味
    """
    
    def __init__(self, config: Optional[ForgeConfig] = None, project_path: Optional[str] = None):
        self.config = config or ForgeConfig()
        self.llm = LLMClient(self.config)
        self.project_path = Path(project_path) if project_path else None
        self.project: Optional[NovelProject] = None
        
        self.orchestrator: Optional[OrchestratorAgent] = None
        self.long_term_memory: Optional[LongTermMemory] = None
        self.aigc_detector: Optional[AIGCDetector] = None
        
        self.craft_rules = CraftRules()
        self.anti_slop = AntiSlopRules()
    
    def load_project(self, project_path: str) -> NovelProject:
        """加载现有项目"""
        self.project_path = Path(project_path)
        self.project = NovelManager.load_project(self.project_path)
        self._init_agents()
        return self.project
    
    def create_project(
        self,
        title: str,
        genre: str,
        synopsis: str,
        target_chapters: int = 1000,
        target_words_per_chapter: int = 3000,
        output_dir: str = "./novels"
    ) -> NovelProject:
        """创建新项目"""
        self.project_path = Path(output_dir) / self._sanitize_title(title)
        self.project = NovelManager.create_project(
            title=title,
            genre=genre,
            synopsis=synopsis,
            target_chapters=target_chapters,
            target_words_per_chapter=target_words_per_chapter,
            output_dir=output_dir
        )
        self._init_agents()
        return self.project
    
    def _init_agents(self):
        """初始化Agent系统"""
        if self.project:
            self.orchestrator = OrchestratorAgent(self.project, self.llm, self.config)
            self.long_term_memory = LongTermMemory(self.project)
            self.aigc_detector = AIGCDetector()
    
    @staticmethod
    def _sanitize_title(title: str) -> str:
        """清理标题作为目录名"""
        import re
        return re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    
    def generate_settings(
        self,
        themes: Optional[List[str]] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        生成世界观和角色设定
        
        Args:
            themes: 核心主题列表
            custom_settings: 自定义设定
            
        Returns:
            生成的设定文件内容字典
        """
        if not self.orchestrator:
            raise RuntimeError("请先加载或创建项目")
        
        return self.orchestrator.generate_foundation(
            themes=themes or ["成长", "复仇", "力量"],
            custom_settings=custom_settings
        )
    
    def generate_outline(
        self,
        num_volumes: int = 10,
        chapters_per_volume: int = 100,
        arc_structure: str = "three_act"
    ) -> str:
        """
        生成全书大纲
        
        Args:
            num_volumes: 卷数
            chapters_per_volume: 每卷章节数
            arc_structure: 故事结构（三幕/英雄之旅等）
            
        Returns:
            大纲文件路径
        """
        if not self.orchestrator:
            raise RuntimeError("请先加载或创建项目")
        
        return self.orchestrator.generate_outline(
            num_volumes=num_volumes,
            chapters_per_volume=chapters_per_volume,
            arc_structure=arc_structure
        )
    
    def write_chapter(
        self,
        chapter_num: int,
        volume_num: int = 1,
        guidance: str = "",
        auto_audit: bool = True,
        auto_revise: bool = True,
        max_revisions: int = 3
    ) -> Dict[str, Any]:
        """
        写作单章
        
        Args:
            chapter_num: 章节号
            volume_num: 卷号
            guidance: 章节指导
            auto_audit: 自动审计
            auto_revise: 自动修订
            max_revisions: 最大修订轮数
            
        Returns:
            写作结果字典
        """
        if not self.orchestrator:
            raise RuntimeError("请先加载或创建项目")
        
        return self.orchestrator.write_chapter(
            chapter_num=chapter_num,
            volume_num=volume_num,
            guidance=guidance,
            auto_audit=auto_audit,
            auto_revise=auto_revise,
            max_revisions=max_revisions
        )
    
    def batch_write(
        self,
        start_chapter: int,
        end_chapter: int,
        volume_num: int = 1,
        guidance: str = "",
        checkpoint_interval: int = 5
    ) -> List[Dict[str, Any]]:
        """
        批量写作
        
        Args:
            start_chapter: 起始章节
            end_chapter: 结束章节
            volume_num: 卷号
            guidance: 全局指导
            checkpoint_interval: 检查点间隔
            
        Returns:
            各章节写作结果列表
        """
        if not self.orchestrator:
            raise RuntimeError("请先加载或创建项目")
        
        results = []
        for ch in range(start_chapter, end_chapter + 1):
            result = self.write_chapter(
                chapter_num=ch,
                volume_num=volume_num,
                guidance=guidance
            )
            results.append(result)
            
            if ch % checkpoint_interval == 0:
                self.project.save()
        
        return results
    
    def audit_chapter(self, chapter_num: int, volume_num: int = 1) -> Dict[str, Any]:
        """审计指定章节"""
        if not self.orchestrator:
            raise RuntimeError("请先加载或创建项目")
        
        return self.orchestrator.audit_chapter(chapter_num, volume_num)
    
    def revise_chapter(
        self,
        chapter_num: int,
        volume_num: int = 1,
        mode: str = "polish"
    ) -> Dict[str, Any]:
        """
        修订指定章节
        
        Args:
            chapter_num: 章节号
            volume_num: 卷号
            mode: 修订模式 (polish/rewrite/rework/anti-detect)
        """
        if not self.orchestrator:
            raise RuntimeError("请先加载或创建项目")
        
        return self.orchestrator.revise_chapter(chapter_num, volume_num, mode)
    
    def track_hooks(self) -> Dict[str, Any]:
        """追踪伏笔状态"""
        if not self.long_term_memory:
            raise RuntimeError("请先加载或创建项目")
        
        return self.long_term_memory.get_hook_status()
    
    def detect_aigc(
        self,
        chapter_num: Optional[int] = None,
        volume_num: Optional[int] = None,
        full_novel: bool = False
    ) -> Dict[str, Any]:
        """
        AIGC检测
        
        Args:
            chapter_num: 章节号（可选）
            volume_num: 卷号（可选）
            full_novel: 是否检测全书
            
        Returns:
            检测报告
        """
        if not self.project:
            raise RuntimeError("请先加载或创建项目")
        
        return self.aigc_detector.detect(
            project=self.project,
            chapter_num=chapter_num,
            volume_num=volume_num,
            full_novel=full_novel
        )
    
    def export_book(self, format: str = "markdown", output_path: Optional[str] = None) -> str:
        """
        导出书籍
        
        Args:
            format: 导出格式 (markdown/text/epub)
            output_path: 输出路径
            
        Returns:
            导出文件路径
        """
        if not self.project:
            raise RuntimeError("请先加载或创建项目")
        
        return NovelManager.export_novel(
            self.project,
            format=format,
            output_path=output_path
        )
    
    def get_status(self) -> Dict[str, Any]:
        """获取项目状态"""
        if not self.project:
            return {"status": "no_project_loaded"}
        
        return {
            "title": self.project.title,
            "genre": self.project.genre,
            "total_chapters": self.project.total_chapters,
            "written_chapters": len(self.project.chapters),
            "current_volume": self.project.current_volume,
            "word_count": sum(getattr(ch, "word_count", 0) for ch in self.project.chapters.values()),
            "pending_hooks": self.track_hooks().get("pending_count", 0),
            "project_path": str(self.project_path)
        }
    
    def get_memory_context(self, chapter_num: int, volume_num: int = 1) -> Dict[str, str]:
        """获取写作上下文记忆"""
        if not self.long_term_memory:
            raise RuntimeError("请先加载或创建项目")
        
        return self.long_term_memory.get_context_for_chapter(chapter_num, volume_num)


def create_forge(config_path: Optional[str] = None) -> NovelForge:
    """
    工厂函数：创建NovelForge实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        NovelForge实例
    """
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        config = ForgeConfig(**config_data)
    else:
        config = ForgeConfig()
    
    return NovelForge(config)
