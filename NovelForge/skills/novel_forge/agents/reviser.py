"""
修订者Agent - 修改优化
"""

from typing import Dict, List, Optional, Any
from ..rules.anti_slop import AntiSlopRules


class ReviserAgent:
    """
    修订者Agent
    
    负责根据审计报告修改优化章节：
    - polish: 润色
    - rewrite: 重写
    - rework: 改造
    - anti-detect: 反检测改写
    """
    
    def __init__(self, llm_client, project, anti_slop: Optional[AntiSlopRules] = None):
        self.llm = llm_client
        self.project = project
        self.anti_slop = anti_slop or AntiSlopRules()
    
    def revise(
        self,
        original: str,
        audit_report: Dict[str, Any],
        mode: str = "polish",
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        修订章节
        
        Args:
            original: 原文
            audit_report: 审计报告
            mode: 修订模式
            max_iterations: 最大迭代次数
            
        Returns:
            修订结果
        """
        result = {
            "original": original,
            "revised": original,
            "iterations": 0,
            "changes": [],
            "final_audit": None
        }
        
        current = original
        
        for i in range(max_iterations):
            result["iterations"] = i + 1
            
            if mode == "polish":
                revised = self._polish(current, audit_report)
            elif mode == "rewrite":
                revised = self._rewrite(current, audit_report)
            elif mode == "rework":
                revised = self._rework(current, audit_report)
            elif mode == "anti-detect":
                revised = self._anti_detect(current)
            else:
                revised = current
            
            if revised == current:
                break
            
            quick_audit = self._quick_audit(revised)
            
            result["changes"].append({
                "iteration": i + 1,
                "preview": revised[:500] + "...",
                "audit": quick_audit
            })
            
            if quick_audit.get("pass"):
                result["revised"] = revised
                result["final_audit"] = quick_audit
                break
            
            current = revised
        
        if not result["final_audit"]:
            result["revised"] = current
            result["final_audit"] = self._quick_audit(current)
        
        return result
    
    def _polish(self, original: str, audit_report: Dict[str, Any]) -> str:
        """润色模式：轻微修改"""
        issues = audit_report.get("issues", [])[:5]
        warnings = audit_report.get("warnings", [])[:5]
        
        if not issues and not warnings:
            return original
        
        feedback_lines = ["# 润色任务\n\n请对以下章节进行润色，修改以下问题：\n"]
        
        for issue in issues:
            feedback_lines.append(f"- {issue.get('suggestion', issue.get('message', ''))}")
        
        for warning in warnings:
            feedback_lines.append(f"- {warning.get('suggestion', warning.get('message', ''))}")
        
        feedback_lines.extend([
            "",
            "要求：",
            "1. 只修改必要部分，保留原文优点",
            "2. 保持文风和字数",
            "3. 不引入新问题",
            "",
            f"# 原文\n{original}"
        ])
        
        system_prompt = """你是一位专业编辑，负责对章节进行润色修改。

规则：
1. 只修改必要部分，保留原文优点
2. 保持原文文风和字数
3. 修复指出的问题
4. 不引入新问题
5. 直接输出修改后的内容，不要解释

直接输出修改后的章节正文。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": "\n".join(feedback_lines)}],
            system=system_prompt,
            temperature=0.5,
            max_tokens=6000
        )
        
        return response.content
    
    def _rewrite(self, original: str, audit_report: Dict[str, Any]) -> str:
        """重写模式：部分重写"""
        feedback = audit_report.get("recommendations", [])
        
        system_prompt = """你是一位专业写手，负责根据反馈重写章节。

规则：
1. 理解并修复反馈指出的所有问题
2. 保持原文的核心情节和角色
3. 改善文风，减少AI特征
4. 直接输出重写后的内容

直接输出重写后的章节正文。"""
        
        user_prompt = f"""# 原文
{original[:3000]}

# 修订反馈
{"".join([f"- {r}\n" for r in feedback[:10]])}

请根据以上反馈重写章节。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.7,
            max_tokens=6000
        )
        
        return response.content
    
    def _rework(self, original: str, audit_report: Dict[str, Any]) -> str:
        """改造模式：大幅修改"""
        system_prompt = """你是一位资深作家，负责对章节进行改造。

要求：
1. 深度修复所有反馈问题
2. 改善整体结构和节奏
3. 增强情感张力和细节描写
4. 完全消除AI特征
5. 保持章节长度

直接输出改造后的章节正文。"""
        
        user_prompt = f"""# 原文
{original[:3000]}

# 审计报告
{self._format_audit_report(audit_report)}

请对以上章节进行改造，直接输出结果。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.8,
            max_tokens=6000
        )
        
        return response.content
    
    def _anti_detect(self, text: str) -> str:
        """反检测模式：消除AI特征"""
        aigc_report = self.anti_slop.full_detect(text)
        guidance = self.anti_slop.get_revision_guidance(aigc_report)
        
        system_prompt = """你是一位语言风格专家，负责消除文本中的AI特征。

AI写作有以下特征，请彻底消除：
1. Tier 1词汇：delve, utilize, leverage, facilitate等
2. Tier 2词汇过度使用
3. "不只是X，而是Y"句式
4. 段落长度过于均匀
5. 句子长度过于均匀
6. 每个段落以过渡词开头
7. 缺乏意外性和个性

人类写作特点：
- 具体名词替代抽象名词
- 句长变化大
- 用词有个性
- 直接表达，避免套话
- 段落长度自然变化

直接输出修改后的文本，不要解释。"""
        
        user_prompt = f"""# 原文
{text}

# AI检测报告
{guidance}

请彻底消除AI特征，输出更像人类写作的版本。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.9,
            max_tokens=6000
        )
        
        return response.content
    
    def _quick_audit(self, text: str) -> Dict[str, Any]:
        """快速审计"""
        aigc_report = self.anti_slop.full_detect(text)
        summary = aigc_report.get("summary", {})
        
        return {
            "pass": not summary.get("needs_revision", False),
            "risk_level": summary.get("risk_level", "UNKNOWN"),
            "critical_issues": summary.get("critical_issues", 0),
            "warning_issues": summary.get("warning_issues", 0),
            "tier1_count": len(aigc_report.get("tier1_critical", [])),
            "tier2_clusters": len(aigc_report.get("tier2_suspicious", {}).get("clusters", []))
        }
    
    def _format_audit_report(self, report: Dict[str, Any]) -> str:
        """格式化审计报告"""
        lines = ["## 审计报告\n"]
        
        issues = report.get("issues", [])
        if issues:
            lines.append("\n### 严重问题")
            for issue in issues:
                lines.append(f"- {issue.get('message', '')}")
                if issue.get("suggestion"):
                    lines.append(f"  建议: {issue['suggestion']}")
        
        warnings = report.get("warnings", [])
        if warnings:
            lines.append("\n### 警告")
            for warning in warnings:
                lines.append(f"- {warning.get('message', '')}")
        
        scores = report.get("scores", {})
        if scores:
            lines.append("\n### 评分")
            for dim, score in scores.items():
                lines.append(f"- {dim}: {score:.1f}/10")
        
        return "\n".join(lines)
    
    def apply_surgical_fix(
        self,
        original: str,
        fix_description: str
    ) -> str:
        """
        精准修复：只修改指定部分
        
        Args:
            original: 原文
            fix_description: 修复描述
            
        Returns:
            修复后内容
        """
        system_prompt = """你是一位专业编辑，负责进行精准修复。

要求：
1. 只修改修复描述中指出的部分
2. 不改动其他内容
3. 保持文风一致
4. 直接输出修改后的内容

直接输出修改后的章节正文。"""
        
        user_prompt = f"""# 原文
{original}

# 修复描述
{fix_description}

请根据上述描述进行精准修复。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.3,
            max_tokens=6000
        )
        
        return response.content
    
    def expand_section(
        self,
        original: str,
        target_section: str,
        expansion_guidance: str
    ) -> str:
        """
        扩展章节部分
        
        Args:
            original: 原文
            target_section: 目标部分描述
            expansion_guidance: 扩展指导
            
        Returns:
            扩展后内容
        """
        system_prompt = """你是一位专业写手，负责扩展章节的特定部分。

规则：
1. 只扩展指定的部分
2. 扩展要自然，符合上下文
3. 增加细节描写和情感深度
4. 不改变整体结构和节奏
5. 直接输出扩展后的内容

直接输出扩展后的章节正文。"""
        
        user_prompt = f"""# 原文
{original}

# 需要扩展的部分
{target_section}

# 扩展指导
{expansion_guidance}

请扩展上述部分，直接输出扩展后的章节正文。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.7,
            max_tokens=8000
        )
        
        return response.content
    
    def compress_section(
        self,
        original: str,
        target_section: str,
        compression_ratio: float = 0.5
    ) -> str:
        """
        压缩章节部分
        
        Args:
            original: 原文
            target_section: 目标部分描述
            compression_ratio: 压缩比例
            
        Returns:
            压缩后内容
        """
        system_prompt = f"""你是一位专业编辑，负责压缩章节的特定部分。

规则：
1. 只压缩指定的部分，保留核心内容
2. 压缩到原来的{int(compression_ratio * 100)}%
3. 保持情节完整
4. 消除冗余
5. 直接输出压缩后的内容

直接输出压缩后的章节正文。"""
        
        user_prompt = f"""# 原文
{original}

# 需要压缩的部分
{target_section}

请压缩上述部分，直接输出压缩后的章节正文。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.3,
            max_tokens=4000
        )
        
        return response.content
