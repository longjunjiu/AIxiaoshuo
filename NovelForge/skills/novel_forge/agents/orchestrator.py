"""
编排器Agent - 流程控制
"""

from typing import Dict, List, Optional, Any
from pathlib import Path

from .architect import ArchitectAgent, ChapterOutlineResult
from .writer import WriterAgent, WritingContext
from .auditor import AuditorAgent
from .reviser import ReviserAgent
from ..memory.long_term import LongTermMemory
from ..memory.mid_term import MidTermMemory
from ..memory.short_term import ShortTermMemory
from ..rules.craft import CraftRules
from ..rules.anti_slop import AntiSlopRules


class OrchestratorAgent:
    """编排器Agent"""
    
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
        """生成基础设定"""
        system_prompt = """你是一位专业的小说策划师，负责创建小说的基础设定。

请根据以下信息生成：
1. 世界观设定（地理、历史、社会、势力）
2. 角色设定（主角、配角、反派）
3. 体系设定（力量系统/修炼体系）
4. 特殊设定（独特规则/法则）

格式：使用Markdown输出，每个部分用二级标题分隔。

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
        
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": user_prompt}],
                system=system_prompt,
                temperature=0.8,
                max_tokens=8000
            )
            settings_content = response.content
        except Exception as e:
            settings_content = f"# {self.project.title} 设定\n\n（需要配置LLM生成完整设定）"
        
        settings_path = Path(self.project.project_path) / "settings"
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
        """生成全书大纲"""
        outline_path = Path(self.project.project_path) / "volumes/volume_1/outline.md"
        outline_path.parent.mkdir(parents=True, exist_ok=True)
        
        outline_content = f"""# {self.project.title} - 大纲

## 第一卷：开局

- 第1章：主角出场，面临困境
- 第2章：金手指出现
- 第3章：第一次小高潮
- ...

## 故事主线

（待详细规划）

## 伏笔设计

（待植入）
"""
        
        try:
            for vol_num in range(1, num_volumes + 1):
                vol_path = Path(self.project.project_path) / f"volumes/volume_{vol_num}"
                vol_path.mkdir(parents=True, exist_ok=True)
                (vol_path / "chapters").mkdir(exist_ok=True)
                (vol_path / "memory").mkdir(exist_ok=True)
            
            self.long_term.save()
        except Exception as e:
            pass
        
        with open(outline_path, 'w', encoding='utf-8') as f:
            f.write(outline_content)
        
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
        """写作单章"""
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
        
        outline_result = self.architect.plan_chapter(
            chapter_num=chapter_num,
            volume_num=volume_num,
            guidance=guidance
        )
        result["outline"] = outline_result
        
        writing_context = WritingContext(
            chapter_title=outline_result.title,
            chapter_num=chapter_num,
            volume_num=volume_num,
            genre=self.project.genre or "玄幻",
            tone="热血",
            target_word_count=self.project.target_words_per_chapter or 3000,
            pov="第三人称"
        )
        writing_context.outline = outline_result
        
        pre_check = self.writer.pre_write_check(writing_context)
        result["pre_check"] = pre_check
        
        draft = self.writer.write_chapter(
            context=writing_context,
            style_profile=self.project.style_profile
        )
        result["draft"] = draft
        
        if auto_audit:
            audit = self.auditor.audit_chapter(
                chapter_num=chapter_num,
                draft=draft
            )
            result["audit"] = audit
            
            if not audit.get("pass", True) and auto_revise:
                revised_result = self.reviser.revise(
                    original=draft,
                    audit_report=audit,
                    mode="polish",
                    max_iterations=max_revisions
                )
                result["revisions"] = revised_result.get("changes", [])
                result["final_content"] = revised_result.get("revised", draft)
            else:
                result["final_content"] = draft
        else:
            result["final_content"] = draft
        
        result["word_count"] = len(result["final_content"])
        
        self._save_chapter(chapter_num, volume_num, result)
        
        result["status"] = "completed"
        result["success"] = True
        
        return result
    
    def _save_chapter(
        self,
        chapter_num: int,
        volume_num: int,
        result: Dict[str, Any]
    ):
        """保存章节"""
        from ..novel_manager import Chapter
        
        ch_dir = Path(self.project.project_path) / f"volumes/volume_{volume_num}/chapters"
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
    
    def batch_write(
        self,
        start_chapter: int,
        end_chapter: int,
        volume_num: int = 1,
        guidance: str = "",
        checkpoint_interval: int = 5
    ) -> List[Dict[str, Any]]:
        """批量写作"""
        results = []
        
        for ch in range(start_chapter, end_chapter + 1):
            print(f"正在写作第{ch}章...")
            
            result = self.write_chapter(
                chapter_num=ch,
                volume_num=volume_num,
                guidance=guidance
            )
            results.append(result)
            
            if ch % checkpoint_interval == 0:
                self.project.save()
                print(f"已保存检查点: 第{ch}章")
        
        return results
    
    def audit_chapter(self, chapter_num: int, volume_num: int = 1) -> Dict[str, Any]:
        """审计章节"""
        ch_path = Path(self.project.project_path) / f"volumes/volume_{volume_num}/chapters/ch_{chapter_num:03d}.md"
        
        if not ch_path.exists():
            return {"error": f"章节文件不存在: {ch_path}"}
        
        with open(ch_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.auditor.audit_chapter(chapter_num=chapter_num, draft=content)
    
    def revise_chapter(
        self,
        chapter_num: int,
        volume_num: int = 1,
        mode: str = "polish"
    ) -> Dict[str, Any]:
        """修订章节"""
        ch_path = Path(self.project.project_path) / f"volumes/volume_{volume_num}/chapters/ch_{chapter_num:03d}.md"
        
        if not ch_path.exists():
            return {"error": f"章节文件不存在: {ch_path}"}
        
        with open(ch_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        audit = self.auditor.audit_chapter(chapter_num=chapter_num, draft=content)
        
        revised_result = self.reviser.revise(
            original=content,
            audit_report=audit,
            mode=mode
        )
        
        revised_content = revised_result.get("revised", content)
        
        with open(ch_path, 'w', encoding='utf-8') as f:
            f.write(revised_content)
        
        return {
            "success": True,
            "chapter": chapter_num,
            "changes": revised_result.get("changes", [])
        }
