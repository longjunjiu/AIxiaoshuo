"""
编排器Agent - 流程控制
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from .architect import ArchitectAgent
from .writer import WriterAgent
from .auditor import AuditorAgent
from .reviser import ReviserAgent
from ..memory.long_term import LongTermMemory
from ..memory.mid_term import MidTermMemory
from ..memory.short_term import ShortTermMemory, WritingContext, ChapterOutline
from ..rules.craft import CraftRules
from ..rules.anti_slop import AntiSlopRules


class OrchestratorAgent:
    """
    编排器Agent
    
    负责协调所有Agent，管理创作流程：
    - 初始化创作环境
    - 编排章节写作流程
    - 管理记忆更新
    - 处理异常和回退
    """
    
    def __init__(self, project, llm_client, config):
        self.project = project
        self.llm = llm_client
        self.config = config
        
        self.craft = CraftRules()
        self.anti_slop = AntiSlopRules()
        
        self.architect = ArchitectAgent(llm_client)
        self.writer = WriterAgent(llm_client, project, self.craft, self.anti_slop)
        self.auditor = AuditorAgent(llm_client, project, self.anti_slop)
        self.reviser = ReviserAgent(llm_client, project, self.anti_slop)
        
        self.long_term = LongTermMemory(project)
        self.short_term = ShortTermMemory()
        self.mid_term = MidTermMemory(project, project.current_volume)
    
    def generate_foundation(
        self,
        themes: Optional[List[str]] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        生成基础设定（世界观、角色等）
        
        Args:
            themes: 核心主题
            custom_settings: 自定义设定
            
        Returns:
            生成的设定文件内容字典
        """
        system_prompt = """你是一位专业的小说策划师，负责创建小说的基础设定。

请根据以下信息生成：
1. 世界观设定（地理、历史、社会、势力）
2. 角色设定（主角、配角、反派）
3. 体系设定（力量系统/修炼体系）
4. 特殊设定（独特规则/法则）

格式：
使用Markdown输出，每个部分用二级标题分隔。

请确保：
- 世界观与题材契合
- 角色有鲜明的性格和动机
- 体系设定有克制和代价
- 所有设定相互关联，形成整体"""
        
        user_prompt = f"""# 小说信息

书名：{self.project.title}
题材：{self.project.genre}
简介：{self.project.synopsis}
目标章节数：{self.project.target_chapters}
目标每章字数：{self.project.target_words_per_chapter}
"""
        
        if themes:
            user_prompt += f"\n核心主题：{', '.join(themes)}\n"
        
        if custom_settings:
            user_prompt += f"\n自定义设定：\n{custom_settings}\n"
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.8,
            max_tokens=8000
        )
        
        settings_content = response.content
        
        settings_path = self.project.project_path / "settings"
        settings_path.mkdir(parents=True, exist_ok=True)
        
        self._parse_and_save_settings(settings_content, settings_path)
        
        return {
            "world": settings_content,
            "status": "foundation_generated"
        }
    
    def _parse_and_save_settings(self, content: str, settings_path: Path):
        """解析并保存设定"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line.replace('## ', '').strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        for section_name, section_content in sections.items():
            filename = f"{section_name.lower().replace(' ', '_')}.md"
            filepath = settings_path / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {section_name}\n\n{section_content}")
    
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
            arc_structure: 故事结构
            
        Returns:
            大纲文件路径
        """
        system_prompt = """你是一位专业的小说策划师，负责规划长篇小说的整体结构。

请根据设定文件生成：
1. 卷大纲（每卷的核心事件和转折）
2. 章节概要（每章的核心内容）
3. 伏笔网络（全书的伏笔布局）

格式：
使用Markdown输出，包含：
- 卷结构
- 每卷章节概要
- 伏笔分布图

请确保：
- 整体结构符合Save the Cat节拍表
- 每卷有明确的核心冲突和解决
- 伏笔分布合理，有植入有回收
- 节奏有起伏，有高潮有缓冲"""
        
        world_content = ""
        world_path = self.project.project_path / "settings/world.md"
        if world_path.exists():
            world_content = world_path.read_text(encoding='utf-8')
        
        user_prompt = f"""# 小说信息

书名：{self.project.title}
题材：{self.project.genre}
总章节数：{num_volumes * chapters_per_volume}
每卷章节数：{chapters_per_volume}
故事结构：{arc_structure}

# 世界观设定
{world_content}

请生成完整的章节大纲。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.7,
            max_tokens=12000
        )
        
        outline_content = response.content
        
        for vol_num in range(1, num_volumes + 1):
            vol_path = self.project.project_path / f"volumes/volume_{vol_num}"
            vol_path.mkdir(parents=True, exist_ok=True)
            (vol_path / "chapters").mkdir(exist_ok=True)
            (vol_path / "memory").mkdir(exist_ok=True)
        
        outline_path = self.project.project_path / f"volumes/volume_1/outline.md"
        with open(outline_path, 'w', encoding='utf-8') as f:
            f.write(outline_content)
        
        self.long_term.save()
        
        return str(outline_path)
    
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
            写作结果
        """
        result = {
            "chapter": chapter_num,
            "volume": volume_num,
            "status": "in_progress",
            "outline": None,
            "draft": None,
            "audit": None,
            "revisions": [],
            "final_content": None,
            "word_count": 0,
            "success": False
        }
        
        self.mid_term = MidTermMemory(self.project, volume_num)
        
        context = self._prepare_context(chapter_num, volume_num)
        
        result["outline"] = self.architect.plan_chapter(
            chapter_num=chapter_num,
            volume_num=volume_num,
            guidance=guidance,
            context=context
        )
        self.short_term.set_outline(result["outline"])
        
        pre_check = self.writer.pre_write_check(self.short_term.context)
        result["pre_check"] = pre_check
        
        draft = self.writer.write_chapter(
            context=self.short_term.context,
            style_profile=self.project.style_profile
        )
        result["draft"] = draft
        self.short_term.set_draft(draft)
        
        if auto_audit:
            audit = self.auditor.audit_chapter(
                chapter_num=chapter_num,
                draft=draft,
                context=context
            )
            result["audit"] = audit
            
            if not audit.get("pass") and auto_revise:
                revised = self.reviser.revise(
                    original=draft,
                    audit_report=audit,
                    mode="polish",
                    max_iterations=max_revisions
                )
                result["revisions"] = revised.get("changes", [])
                result["final_content"] = revised.get("revised", draft)
            else:
                result["final_content"] = draft
        else:
            result["final_content"] = draft
        
        result["word_count"] = len(result["final_content"])
        
        self._save_chapter(chapter_num, volume_num, result)
        self._update_memory(chapter_num, volume_num, result)
        
        result["status"] = "completed"
        result["success"] = True
        
        return result
    
    def _prepare_context(
        self,
        chapter_num: int,
        volume_num: int
    ) -> Dict[str, Any]:
        """准备写作上下文"""
        long_term_context = self.long_term.get_context_for_chapter(chapter_num, volume_num)
        
        mid_term_context = self.mid_term.get_chapter_context(chapter_num)
        
        character_states = {}
        for char, state in self.long_term.character_states.items():
            character_states[char] = f"位置: {state.location}, 状态: {state.emotional_state}"
        
        pending_hooks = [
            {"id": h.id, "content": h.content}
            for h in self.long_term.hooks.values()
            if h.status == "pending"
        ]
        
        outline = ChapterOutline(
            chapter_num=chapter_num,
            title=f"第{chapter_num}章",
            synopsis="",
            scenes=[]
        )
        
        writing_context = WritingContext(
            chapter_num=chapter_num,
            volume_num=volume_num,
            outline=outline,
            long_term_context=long_term_context,
            mid_term_context=mid_term_context,
            character_states=character_states,
            pending_hooks=pending_hooks
        )
        
        self.short_term.set_context(writing_context)
        
        return {
            "long_term": long_term_context,
            "mid_term": mid_term_context,
            "character_states": character_states,
            "pending_hooks": pending_hooks
        }
    
    def _save_chapter(
        self,
        chapter_num: int,
        volume_num: int,
        result: Dict[str, Any]
    ):
        """保存章节"""
        from ..novel_manager import Chapter
        
        ch_dir = self.project.project_path / f"volumes/volume_{volume_num}/chapters"
        ch_dir.mkdir(parents=True, exist_ok=True)
        
        chapter = Chapter(
            number=chapter_num,
            title=result["outline"].title,
            content=result["final_content"],
            word_count=result["word_count"],
            status="final"
        )
        
        filepath = ch_dir / f"ch_{chapter_num:03d}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {chapter.title}\n\n{chapter.content}")
        
        self.project.chapters[chapter_num] = chapter
        self.project.total_chapters = max(self.project.total_chapters, chapter_num)
        self.project.save()
    
    def _update_memory(
        self,
        chapter_num: int,
        volume_num: int,
        result: Dict[str, Any]
    ):
        """更新记忆"""
        post_settlement = self.writer.post_write_settlement(
            result["final_content"],
            result["outline"]
        )
        
        self.mid_term.add_summary(
            chapter_num=chapter_num,
            title=result["outline"].title,
            characters=[],
            events=[],
            state_changes=[]
        )
        
        self.long_term.save()
        self.mid_term.save()
    
    def batch_write(
        self,
        start_chapter: int,
        end_chapter: int,
        volume_num: int = 1,
        checkpoint_interval: int = 5
    ) -> List[Dict[str, Any]]:
        """
        批量写作
        
        Args:
            start_chapter: 起始章节
            end_chapter: 结束章节
            volume_num: 卷号
            checkpoint_interval: 检查点间隔
            
        Returns:
            各章节结果列表
        """
        results = []
        
        for ch in range(start_chapter, end_chapter + 1):
            print(f"正在写作第{ch}章...")
            
            result = self.write_chapter(
                chapter_num=ch,
                volume_num=volume_num,
                guidance=""
            )
            results.append(result)
            
            if ch % checkpoint_interval == 0:
                self.project.save()
                print(f"已保存检查点: 第{ch}章")
        
        return results
    
    def rollback_chapter(
        self,
        chapter_num: int,
        volume_num: int = 1
    ) -> bool:
        """
        回滚章节
        
        Args:
            chapter_num: 章节号
            volume_num: 卷号
            
        Returns:
            是否成功
        """
        ch_path = self.project.project_path / f"volumes/volume_{volume_num}/chapters"
        
        backup_path = ch_path / f"ch_{chapter_num:03d}.md.bak"
        original_path = ch_path / f"ch_{chapter_num:03d}.md"
        
        if backup_path.exists():
            import shutil
            shutil.copy(backup_path, original_path)
            backup_path.unlink()
            return True
        
        return False
