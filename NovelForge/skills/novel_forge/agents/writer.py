"""
写手Agent - 生成正文
"""

from typing import Dict, List, Optional, Any
from ..memory.short_term import ChapterOutline, WritingContext
from ..rules.craft import CraftRules
from ..rules.anti_slop import AntiSlopRules


class WriterAgent:
    """
    写手Agent
    
    负责根据大纲生成正文，实现：
    - 文风一致性
    - 去AI味
    - 上下文连贯
    """
    
    def __init__(
        self,
        llm_client,
        project,
        craft_rules: Optional[CraftRules] = None,
        anti_slop: Optional[AntiSlopRules] = None
    ):
        self.llm = llm_client
        self.project = project
        self.craft = craft_rules or CraftRules()
        self.anti_slop = anti_slop or AntiSlopRules()
    
    def write_chapter(
        self,
        context: WritingContext,
        style_profile: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        写作章节
        
        Args:
            context: 写作上下文
            style_profile: 风格指纹
            
        Returns:
            章节正文
        """
        system_prompt = self._get_system_prompt(style_profile)
        user_prompt = self._build_writing_prompt(context)
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.8,
            max_tokens=8000
        )
        
        return response.content
    
    def _get_system_prompt(self, style_profile: Optional[Dict[str, Any]]) -> str:
        """获取系统提示"""
        base_rules = self.craft.get_all_rules_prompt()
        anti_slop_rules = self.anti_slop.get_revision_guidance(
            self.anti_slop.full_detect("")
        )
        
        prompt = f"""你是一位专业的网络小说写手，负责根据大纲生成高质量正文。

## 核心要求

1. **文风自然**: 避免AI味，使用生动具体的描写
2. **细节丰富**: 具体名词替代抽象名词
3. **节奏感强**: 短句营造紧张，长句描述舒缓
4. **对话生动**: 对话推动剧情，体现角色性格
5. **伏笔自然**: 伏笔植入要自然，不突兀

## 创作规则
{base_rules}

## 反AI味规则
{anti_slop_rules}

## 章节结构
每个场景应包含：
- 环境描写（简洁，点到即止）
- 角色动作和对话
- 内心活动（适度，不过度）
- 冲突推进

## 禁止事项
- 禁止使用AI常用词汇（delve, utilize, leverage等）
- 禁止每段以过渡词开头
- 禁止"不只是X，而是Y"句式
- 禁止段落长度过于均匀
- 禁止直接描述情绪（"他很愤怒" → "他摔碎了茶杯"）
- 禁止分析报告式语言

## 字数控制
目标{self.project.target_words_per_chapter}字，允许±15%误差"""

        if style_profile:
            prompt += f"\n\n## 风格指纹\n"
            prompt += f"句长偏好: {style_profile.get('avg_sentence_len', '中等')}\n"
            prompt += f"描写密度: {style_profile.get('description_density', '适中')}\n"
            prompt += f"对话比例: {style_profile.get('dialogue_ratio', '适中')}\n"
            prompt += f"特有表达: {style_profile.get('unique_phrases', '无')}\n"
        
        return prompt
    
    def _build_writing_prompt(self, context: WritingContext) -> str:
        """构建写作提示"""
        lines = [
            "# 写作任务",
            "",
            f"## 当前章节",
            f"卷{context.volume_num} 第{context.chapter_num}章：{context.outline.title}",
            "",
            f"## 章节概要",
            context.outline.synopsis,
            "",
            "## 场景大纲"
        ]
        
        for i, scene in enumerate(context.outline.scenes, 1):
            lines.extend([
                f"\n### 场景{i}: {scene.location} | {scene.time}",
                f"**角色**: {', '.join(scene.characters)}",
                f"**目标**: {scene.goal}",
                f"**冲突**: {scene.conflict}"
            ])
        
        lines.extend(["", "## 上下文记忆"])
        
        if context.long_term_context:
            if context.long_term_context.get('relevant_facts'):
                lines.append("\n### 关键事实")
                lines.append(context.long_term_context['relevant_facts'])
            
            if context.long_term_context.get('pending_hooks'):
                lines.append("\n### 伏笔追踪")
                lines.append(context.long_term_context['pending_hooks'])
        
        if context.character_states:
            lines.append("\n### 角色状态")
            for char, state in context.character_states.items():
                lines.append(f"- **{char}**: {state}")
        
        if context.pending_hooks:
            lines.extend(["", "## 本章需回收伏笔"])
            for hook in context.pending_hooks:
                lines.append(f"- [{hook['id']}] {hook['content']}")
        
        if context.outline.hooks_to_plant:
            lines.extend(["", "## 本章需植入伏笔（自然融入）"])
            for hook in context.outline.hooks_to_plant:
                lines.append(f"- {hook}")
        
        if context.outline.resources_to_change:
            lines.extend(["", "## 资源变动（融入叙述）"])
            for res in context.outline.resources_to_change:
                lines.append(f"- {res['resource']}: {res['change']}")
        
        lines.extend([
            "",
            "## 输出要求",
            "直接输出正文，不要输出大纲或其他说明文字。",
            "正文应包含完整的章节内容，结尾留下适当悬念或过渡。"
        ])
        
        return "\n".join(lines)
    
    def pre_write_check(self, context: WritingContext) -> str:
        """
        写前自检
        
        Args:
            context: 写作上下文
            
        Returns:
            自检报告
        """
        check_list = context.generate_pre_write_checklist()
        
        system_prompt = """你是一位审稿编辑，负责在写作前进行自检。

请根据上下文信息，核实以下事项并输出报告：
1. 上下文范围确认
2. 资源状态确认
3. 伏笔待回收确认
4. 潜在冲突点识别
5. 风险评估

直接输出报告，不要写作文。"""
        
        user_prompt = f"# 上下文信息\n\n{check_list}\n\n请完成自检并输出报告。"
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.content
    
    def post_write_settlement(
        self,
        draft: str,
        outline: ChapterOutline
    ) -> str:
        """
        写后结算
        
        Args:
            draft: 草稿
            outline: 章节大纲
            
        Returns:
            结算报告
        """
        settlement = outline.generate_post_write_settlement()
        
        system_prompt = """你是一位审稿编辑，负责在写作后进行结算。

请根据草稿内容，填写以下信息：
1. 资源变动（实际发生的）
2. 伏笔变动（植入/回收情况）
3. 角色状态变化
4. 信息揭露情况

直接输出报告，简洁明了。"""
        
        user_prompt = f"# 大纲要求\n{settlement}\n\n# 实际草稿\n{draft[:3000]}...\n\n请完成结算报告。"
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.3,
            max_tokens=1500
        )
        
        return response.content
    
    def rewrite_section(
        self,
        original: str,
        feedback: str,
        section: str = "full"
    ) -> str:
        """
        重写部分内容
        
        Args:
            original: 原文
            feedback: 反馈意见
            section: 重写范围
            
        Returns:
            重写后内容
        """
        system_prompt = """你是一位专业写手，负责根据反馈重写部分内容。

要求：
1. 保留原文的优点
2. 针对性修改反馈指出的问题
3. 保持文风一致
4. 不引入新问题

直接输出重写后的内容，不要解释。"""
        
        user_prompt = f"# 原文\n{original}\n\n# 反馈\n{feedback}\n\n# 重写范围\n{section}\n\n请重写上述内容。"
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.content
