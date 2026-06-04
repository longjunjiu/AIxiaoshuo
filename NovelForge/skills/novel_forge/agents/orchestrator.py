"""
编排器Agent - 真正的多Agent协作系统
实现Agent间多轮讨论、投票决策、协作优化
"""

import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from .architect import ArchitectAgent, ChapterOutlineResult
from .writer import WriterAgent, WritingContext
from .auditor import AuditorAgent
from .reviser import ReviserAgent
from .panel import PanelAgent, PanelDecision
from ..memory.long_term import LongTermMemory
from ..memory.mid_term import MidTermMemory
from ..memory.short_term import ShortTermMemory
from ..rules.craft import CraftRules
from ..rules.anti_slop import AntiSlopRules


@dataclass
class AgentMessage:
    """Agent消息"""
    sender: str
    receiver: str
    content: str
    timestamp: float = field(default_factory=time.time)
    message_type: str = "proposal"


@dataclass
class AgentDiscussion:
    """Agent讨论记录"""
    topic: str
    messages: List[AgentMessage] = field(default_factory=list)
    iterations: int = 0
    consensus_reached: bool = False


class MultiAgentOrchestrator:
    """
    多Agent协作编排器
    
    协作流程：
    1. 建筑师(Architect) - 提出章节大纲方案
    2. 写手(Writer) - 根据大纲生成初稿
    3. 审计员(Auditor) - 审查初稿质量
    4. 修订者(Reviser) - 根据审计意见修订
    5. 评审团(Panel) - 多视角评审，决定是否通过
    6. 如果不通过，各Agent讨论后重新生成
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
        self.panel = PanelAgent(llm_client)
        
        self.long_term = LongTermMemory(project)
        self.short_term = ShortTermMemory()
        self.mid_term = MidTermMemory(project, project.current_volume)
        
        self.discussion_history: List[AgentDiscussion] = []
    
    # ──────────────────────────────────────────────────────────────
    # 对外接口（供 NovelForge 调用）
    # ──────────────────────────────────────────────────────────────

    def generate_foundation(
        self,
        themes: Optional[List[str]] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """生成世界观和角色设定"""
        themes = themes or ["成长", "复仇", "力量"]
        themes_str = "、".join(themes)
        settings: Dict[str, str] = {}

        if self.llm:
            prompts = {
                "world": (
                    f"请为以下小说生成详细的世界观设定（约1000字）：\n\n"
                    f"书名：{self.project.title}\n题材：{self.project.genre}\n"
                    f"简介：{self.project.synopsis}\n核心主题：{themes_str}\n\n"
                    "请包含：世界概述、地理环境、社会结构、历史背景、势力分布。\n"
                    "直接输出设定内容。",
                    "你是一位顶尖的网文世界观设计师。"
                ),
                "characters": (
                    f"请为以下小说生成详细的角色设定（约1500字）：\n\n"
                    f"书名：{self.project.title}\n题材：{self.project.genre}\n"
                    f"简介：{self.project.synopsis}\n核心主题：{themes_str}\n\n"
                    "请包含：主角详细设定（背景、性格、能力、目标）、3-5位配角、主要反派、势力关系。\n"
                    "直接输出角色设定。",
                    "你是一位顶尖的网文角色设计师。"
                ),
                "system": (
                    f"请为以下小说生成详细的体系设定（约1000字）：\n\n"
                    f"书名：{self.project.title}\n题材：{self.project.genre}\n"
                    f"简介：{self.project.synopsis}\n\n"
                    "请包含：修炼/能力体系、境界划分、技能分类、道具体系。\n"
                    "直接输出体系设定。",
                    "你是一位顶尖的网文体系设计师。"
                ),
            }

            key_labels = {"world": "世界观", "characters": "角色", "system": "体系"}
            for key, (user_prompt, sys_prompt) in prompts.items():
                label = key_labels.get(key, key)
                try:
                    resp = self.llm.chat(
                        messages=[{"role": "user", "content": user_prompt}],
                        system=sys_prompt,
                        temperature=0.8,
                        max_tokens=2500
                    )
                    settings[key] = f"# {self.project.title} - {label}设定\n\n{resp.content}"
                except Exception as e:
                    settings[key] = f"# {self.project.title} - {label}设定\n\n（生成失败：{e}）"
        else:
            for key in ("world", "characters", "system"):
                settings[key] = f"# {self.project.title} - {key}设定\n\n（需要配置 LLM 才能生成）\n"

        if custom_settings:
            settings.update(custom_settings)

        settings_path = Path(self.project.project_path) / "settings"
        settings_path.mkdir(parents=True, exist_ok=True)
        for key, content in settings.items():
            (settings_path / f"{key}.md").write_text(content, encoding="utf-8")
            self.project.world_settings[key] = content

        return settings

    def generate_outline(
        self,
        num_volumes: int = 10,
        chapters_per_volume: int = 100,
        arc_structure: str = "three_act"
    ) -> str:
        """生成全书大纲，返回大纲文件路径"""
        outline_path = Path(self.project.project_path) / "outline.md"

        if self.llm:
            prompt = (
                f"请为以下小说生成详细的全书大纲：\n\n"
                f"书名：{self.project.title}\n题材：{self.project.genre}\n"
                f"简介：{self.project.synopsis}\n"
                f"总卷数：{num_volumes}卷，每卷约{chapters_per_volume}章\n"
                f"故事结构：{arc_structure}\n\n"
                "请按卷输出大纲，每卷包含：卷名、主要情节、核心冲突、结局走向（各卷约200字）。\n"
                "直接输出大纲内容。"
            )
            try:
                resp = self.llm.chat(
                    messages=[{"role": "user", "content": prompt}],
                    system="你是一位顶尖的网文大纲规划师，精通长篇小说的宏观结构设计。",
                    temperature=0.7,
                    max_tokens=4000
                )
                content = f"# {self.project.title} - 全书大纲\n\n{resp.content}"
            except Exception as e:
                content = f"# {self.project.title} - 全书大纲\n\n（生成失败：{e}）\n"
        else:
            content = (
                f"# {self.project.title} - 全书大纲\n\n"
                f"（需要配置 LLM 才能生成）\n\n"
                f"基本信息：{num_volumes}卷 × {chapters_per_volume}章\n"
            )

        outline_path.parent.mkdir(parents=True, exist_ok=True)
        outline_path.write_text(content, encoding="utf-8")

        vol1_outline = Path(self.project.project_path) / "volumes/volume_1/outline.md"
        vol1_outline.parent.mkdir(parents=True, exist_ok=True)
        vol1_outline.write_text(content, encoding="utf-8")

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
        """写作章节（对外接口，委托多Agent流程）"""
        return self.write_chapter_multi_agent(
            chapter_num=chapter_num,
            volume_num=volume_num,
            guidance=guidance,
            max_iterations=max_revisions,
            require_consensus=auto_audit
        )

    def audit_chapter(self, chapter_num: int, volume_num: int = 1) -> Dict[str, Any]:
        """审计章节"""
        ch = self.project.chapters.get(chapter_num)
        if ch:
            content = ch.content if hasattr(ch, "content") else str(ch)
        else:
            ch_file = (
                Path(self.project.project_path)
                / f"volumes/volume_{volume_num}/chapters"
                / f"ch_{chapter_num:03d}.md"
            )
            if ch_file.exists():
                content = ch_file.read_text(encoding="utf-8")
            else:
                return {"error": f"章节 {chapter_num} 不存在", "pass": False}

        return self.auditor.audit_chapter(chapter_num=chapter_num, draft=content)

    def revise_chapter(
        self, chapter_num: int, volume_num: int = 1, mode: str = "polish"
    ) -> Dict[str, Any]:
        """修订并保存章节"""
        ch = self.project.chapters.get(chapter_num)
        if ch:
            content = ch.content if hasattr(ch, "content") else str(ch)
        else:
            ch_file = (
                Path(self.project.project_path)
                / f"volumes/volume_{volume_num}/chapters"
                / f"ch_{chapter_num:03d}.md"
            )
            if ch_file.exists():
                content = ch_file.read_text(encoding="utf-8")
            else:
                return {"error": f"章节 {chapter_num} 不存在", "success": False}

        result = self.reviser.revise(original=content, mode=mode)

        if result.get("success") and result.get("revised"):
            ch_dir = (
                Path(self.project.project_path)
                / f"volumes/volume_{volume_num}/chapters"
            )
            ch_dir.mkdir(parents=True, exist_ok=True)
            (ch_dir / f"ch_{chapter_num:03d}.md").write_text(
                result["revised"], encoding="utf-8"
            )
            if chapter_num in self.project.chapters:
                self.project.chapters[chapter_num].content = result["revised"]
                self.project.chapters[chapter_num].status = "revised"

        return result

    # ──────────────────────────────────────────────────────────────

    def write_chapter_multi_agent(
        self,
        chapter_num: int,
        volume_num: int = 1,
        guidance: str = "",
        max_iterations: int = 3,
        require_consensus: bool = True
    ) -> Dict[str, Any]:
        """
        多Agent协作写作单章
        
        流程：
        ┌─────────────┐
        │  建筑师规划  │  ← 首先设计章节大纲
        └──────┬──────┘
               ↓
        ┌─────────────┐
        │  写手生成    │  ← 根据大纲生成初稿
        └──────┬──────┘
               ↓
        ┌─────────────┐
        │  审计员审查  │  ← 26维度质量检查
        └──────┬──────┘
               ↓
        ┌─────────────┐
        │  修订者修订  │  ← 根据审计意见修订
        └──────┬──────┘
               ↓
        ┌─────────────┐
        │  评审团评审  │  ← 多视角投票决策
        └──────┬──────┘
               ↓
        ┌─────────────┐
        │  通过？      │  ← 评审团投票
        └──────┬──────┘
               ↓
        ┌─────────────┐
        │  多轮讨论    │  ← 如果不通过，Agent讨论优化
        └─────────────┘
        """
        
        print(f"\n{'='*60}")
        print(f"  多Agent协作写作 - 第{chapter_num}章")
        print(f"{'='*60}")
        
        result = {
            "chapter": chapter_num,
            "volume": volume_num,
            "iterations": [],
            "final_content": None,
            "word_count": 0,
            "consensus_reached": False,
            "success": False
        }
        
        for iteration in range(1, max_iterations + 1):
            print(f"\n📍 第 {iteration}/{max_iterations} 轮协作")
            print("-" * 40)
            
            iteration_result = self._single_iteration(
                chapter_num=chapter_num,
                volume_num=volume_num,
                guidance=guidance,
                iteration=iteration
            )
            
            result["iterations"].append(iteration_result)
            
            if iteration_result.get("panel_decision"):
                decision: PanelDecision = iteration_result["panel_decision"]
                
                print(f"\n🎯 评审团决策: {decision.final_verdict}")
                print(f"   综合评分: {decision.overall_score:.1f}/10")
                
                if decision.overall_score >= 7.0 and decision.final_verdict in ("通过", "修改后通过"):
                    result["final_content"] = iteration_result["revised_content"]
                    result["word_count"] = len(result["final_content"])
                    result["consensus_reached"] = True
                    result["success"] = True
                    print(f"\n✅ 章节通过! (第{iteration}轮, {decision.final_verdict})")
                    break
                else:
                    print(f"\n⚠️ 评审团提出改进意见:")
                    for issue in decision.issues[:3]:
                        print(f"   - {issue}")
            else:
                print(f"\n⚠️ 第{iteration}轮未完成评审")
        
        if not result["success"]:
            print(f"\n❌ 达到最大迭代次数({max_iterations})，使用最新版本")
            if result["iterations"]:
                last_iter = result["iterations"][-1]
                result["final_content"] = last_iter.get("revised_content", "")
                result["word_count"] = len(result["final_content"])
        
        self._save_chapter(chapter_num, volume_num, result)
        
        return result
    
    def _single_iteration(
        self,
        chapter_num: int,
        volume_num: int,
        guidance: str,
        iteration: int
    ) -> Dict[str, Any]:
        """单轮迭代"""

        iteration_result = {
            "iteration": iteration,
            "outline": None,
            "draft": None,
            "audit": None,
            "revised_content": None,
            "panel_decision": None,
            "discussion": []
        }

        # Gather memory context before planning
        long_term_ctx = self.long_term.get_context_for_chapter(chapter_num, volume_num)
        mid_term_ctx = self.mid_term.get_chapter_context(chapter_num)
        pending_hooks = self.long_term.get_hook_status().get("pending_hooks", [])

        print("\n[1/5] 建筑师规划章节...")
        outline = self.architect.plan_chapter(
            chapter_num=chapter_num,
            volume_num=volume_num,
            guidance=guidance,
            context={
                "long_term": long_term_ctx,
                "pending_hooks": pending_hooks,
            }
        )
        iteration_result["outline"] = outline
        print(f"   ✅ 大纲: {outline.title}")

        print("\n[2/5] 写手生成初稿...")
        writing_context = WritingContext(
            chapter_title=outline.title,
            chapter_num=chapter_num,
            volume_num=volume_num,
            genre=self.project.genre or "玄幻",
            tone="热血",
            target_word_count=self.project.target_words_per_chapter or 3000,
            pov="第三人称",
            long_term_context=long_term_ctx,
            mid_term_context=mid_term_ctx
        )
        writing_context.outline = outline
        
        draft = self.writer.write_chapter(writing_context)
        iteration_result["draft"] = draft
        print(f"   ✅ 初稿完成 ({len(draft)}字)")
        
        print("\n[3/5] 审计员质量审查...")
        audit = self.auditor.audit_chapter(chapter_num=chapter_num, draft=draft)
        iteration_result["audit"] = audit
        
        if audit.get("issues"):
            print(f"   ⚠️ 发现 {len(audit['issues'])} 个问题")
        else:
            print(f"   ✅ 审计通过")
        
        print("\n[4/5] 修订者修订...")
        revised_result = self.reviser.revise(
            original=draft,
            audit_report=audit,
            mode="polish"
        )
        iteration_result["revised_content"] = revised_result.get("revised", draft)
        print(f"   ✅ 修订完成 ({len(iteration_result['revised_content'])}字)")
        
        print("\n[5/5] 评审团多视角评审...")
        panel_decision = self.panel.review_chapter(
            chapter_num=chapter_num,
            content=iteration_result["revised_content"],
            outline=outline,
            context={
                "genre": self.project.genre,
                "protagonist": getattr(self.project, 'protagonist', None),
                "iteration": iteration
            }
        )
        iteration_result["panel_decision"] = panel_decision
        
        return iteration_result
    
    def agent_discussion(
        self,
        topic: str,
        agents: List[str],
        context: Dict[str, Any]
    ) -> AgentDiscussion:
        """
        Agent间多轮讨论
        
        各Agent轮流发表意见，最终达成共识
        """
        discussion = AgentDiscussion(topic=topic)
        
        print(f"\n💬 Agent讨论: {topic}")
        print("-" * 40)
        
        agent_views = {}
        
        for agent_name in agents:
            print(f"\n  📢 {agent_name} 发表意见...")
            
            if agent_name == "Architect":
                view = self._architect_review(context)
            elif agent_name == "Writer":
                view = self._writer_review(context)
            elif agent_name == "Auditor":
                view = self._auditor_review(context)
            elif agent_name == "Reviser":
                view = self._reviser_review(context)
            else:
                view = "无意见"
            
            agent_views[agent_name] = view
            print(f"     {view[:100]}...")
            
            discussion.messages.append(AgentMessage(
                sender=agent_name,
                receiver="Panel",
                content=view,
                message_type="opinion"
            ))
        
        consensus_prompt = f"""
基于以下Agent的观点，请总结共识：

{chr(10).join([f"{name}: {view}" for name, view in agent_views.items()])}

如果观点一致，返回"共识达成: [总结]"
如果观点不一致，返回"分歧: [列出分歧点]"
"""
        
        try:
            consensus_response = self.llm.chat(
                messages=[{"role": "user", "content": consensus_prompt}],
                system="你是一个讨论协调者，总结各方观点，达成共识。",
                temperature=0.5,
                max_tokens=1000
            )
            
            discussion.messages.append(AgentMessage(
                sender="Panel",
                receiver="all",
                content=consensus_response.content,
                message_type="consensus"
            ))
            
            discussion.consensus_reached = "共识达成" in consensus_response.content
            discussion.iterations += 1
            
            print(f"\n  🎯 协调者: {consensus_response.content[:100]}...")
            
        except Exception as e:
            print(f"  ⚠️ 协调失败: {e}")
        
        self.discussion_history.append(discussion)
        
        return discussion
    
    def _architect_review(self, context: Dict) -> str:
        """建筑师视角审查"""
        content = context.get("content", "")
        outline = context.get("outline", {})
        
        prompt = f"""你是建筑师Agent，负责审查章节结构设计。

大纲：{outline.get('title', '')}

请从以下角度审查：
1. 章节结构是否合理？
2. 核心事件是否突出？
3. 伏笔是否埋设得当？
4. 与整体大纲是否契合？

请给出简短评价。"""
        
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system="你是一个专业的小说架构师。",
                temperature=0.5,
                max_tokens=500
            )
            return response.content[:200]
        except:
            return "结构设计合理"
    
    def _writer_review(self, context: Dict) -> str:
        """写手视角审查"""
        content = context.get("content", "")
        
        prompt = f"""你是写手Agent，负责审查文字表达。

章节片段：
{content[:500]}

请从以下角度审查：
1. 语言是否流畅自然？
2. 对话是否生动？
3. 是否有足够的细节描写？
4. 节奏把控如何？

请给出简短评价。"""
        
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system="你是一个专业的小说作家。",
                temperature=0.5,
                max_tokens=500
            )
            return response.content[:200]
        except:
            return "文笔表达良好"
    
    def _auditor_review(self, context: Dict) -> str:
        """审计员视角审查"""
        content = context.get("content", "")
        
        prompt = f"""你是审计员Agent，负责审查质量合规性。

章节片段：
{content[:500]}

请从以下角度审查：
1. 是否有逻辑漏洞？
2. 是否有AI味？
3. 爽点设计是否到位？
4. 是否有错别字？

请给出简短评价。"""
        
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system="你是一个专业的小说质量审计师。",
                temperature=0.5,
                max_tokens=500
            )
            return response.content[:200]
        except:
            return "质量检查通过"
    
    def _reviser_review(self, context: Dict) -> str:
        """修订者视角审查"""
        content = context.get("content", "")
        
        prompt = f"""你是修订者Agent，负责审查可改进之处。

章节片段：
{content[:500]}

请从以下角度审查：
1. 哪些地方可以更好？
2. 哪些表达需要优化？
3. 是否有更好的爽点设计？

请给出简短评价和建议。"""
        
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                system="你是一个专业的小说文字编辑。",
                temperature=0.5,
                max_tokens=500
            )
            return response.content[:200]
        except:
            return "无需大幅修订"
    
    def batch_write_multi_agent(
        self,
        start_chapter: int,
        end_chapter: int,
        volume_num: int = 1,
        guidance: str = "",
        checkpoint_interval: int = 5
    ) -> List[Dict[str, Any]]:
        """多Agent批量写作"""
        results = []
        
        print(f"\n{'#'*60}")
        print(f"  多Agent批量写作 - 第{start_chapter}章到第{end_chapter}章")
        print(f"{'#'*60}")
        
        for ch in range(start_chapter, end_chapter + 1):
            result = self.write_chapter_multi_agent(
                chapter_num=ch,
                volume_num=volume_num,
                guidance=guidance
            )
            results.append(result)
            
            if ch % checkpoint_interval == 0:
                self.project.save()
                print(f"\n💾 检查点已保存: 第{ch}章")
            
            print(f"\n{'='*60}")
            print(f"第{ch}章完成: {'✅' if result['success'] else '⚠️'}")
            print(f"{'='*60}\n")
        
        return results
    
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
        
        final_content = result.get("final_content", "")
        final_title = "未命名章节"
        
        if result.get("iterations"):
            last_iter = result["iterations"][-1]
            if last_iter.get("outline"):
                final_title = last_iter["outline"].title
        
        chapter = Chapter(
            number=chapter_num,
            title=final_title,
            content=final_content,
            word_count=result.get("word_count", 0),
            status="final" if result["success"] else "draft"
        )
        
        filepath = ch_dir / f"ch_{chapter_num:03d}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {chapter.title}\n\n{chapter.content}")
        
        self.project.chapters[chapter_num] = chapter
        self.project.total_chapters = max(self.project.total_chapters, chapter_num)
        self.project.save()


OrchestratorAgent = MultiAgentOrchestrator
