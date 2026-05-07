"""
审计员Agent - 质量检查
"""

import re
from typing import Dict, List, Optional, Any
from ..rules.anti_slop import AntiSlopRules


class AuditorAgent:
    """
    审计员Agent
    
    负责多维度质量审计：
    - 连续性检查
    - 伏笔检查
    - 节奏检查
    - 文风检查
    - AIGC检测
    """
    
    def __init__(self, llm_client, project, anti_slop: Optional[AntiSlopRules] = None):
        self.llm = llm_client
        self.project = project
        self.anti_slop = anti_slop or AntiSlopRules()
    
    def audit_chapter(
        self,
        chapter_num: int,
        draft: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        审计章节
        
        Args:
            chapter_num: 章节号
            draft: 章节草稿
            context: 上下文信息
            
        Returns:
            审计报告
        """
        results = {
            "chapter": chapter_num,
            "pass": True,
            "issues": [],
            "warnings": [],
            "scores": {},
            "aigc_report": None,
            "recommendations": []
        }
        
        results["aigc_report"] = self.anti_slop.full_detect(draft)
        
        continuity_issues = self._check_continuity(draft, chapter_num, context)
        if continuity_issues:
            results["issues"].extend(continuity_issues)
        
        hook_issues = self._check_hooks(draft, chapter_num, context)
        if hook_issues:
            results["warnings"].extend(hook_issues)
        
        pacing_issues = self._check_pacing(draft)
        if pacing_issues:
            results["warnings"].extend(pacing_issues)
        
        voice_issues = self._check_voice(draft)
        if voice_issues:
            results["issues"].extend(voice_issues)
        
        factual_issues = self._check_facts(draft, chapter_num, context)
        if factual_issues:
            results["issues"].extend(factual_issues)
        
        results["scores"] = self._calculate_scores(results)
        results["pass"] = len([i for i in results["issues"] if i.get("severity") == "critical"]) == 0
        
        results["recommendations"] = self._generate_recommendations(results)
        
        return results
    
    def _check_continuity(
        self,
        draft: str,
        chapter_num: int,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检查连续性"""
        issues = []
        
        if not context:
            return issues
        
        if context.get("character_states"):
            for char, expected_state in context["character_states"].items():
                if char in draft:
                    pass
        
        if context.get("location"):
            location = context["location"]
            location_mentions = len(re.findall(location, draft))
            if location_mentions == 0:
                issues.append({
                    "dimension": "continuity",
                    "type": "location_missing",
                    "severity": "warning",
                    "message": f"未提及场景地点: {location}",
                    "suggestion": "在场景开头明确位置"
                })
        
        return issues
    
    def _check_hooks(
        self,
        draft: str,
        chapter_num: int,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检查伏笔"""
        warnings = []
        
        if not context or not context.get("pending_hooks"):
            return warnings
        
        for hook in context["pending_hooks"]:
            hook_content = hook.get("content", "")
            if hook_content and hook_content[:20] in draft:
                warnings.append({
                    "dimension": "foreshadow",
                    "type": "hook_recycled",
                    "severity": "info",
                    "message": f"伏笔可能已回收: {hook_content[:30]}...",
                    "hook_id": hook.get("id")
                })
        
        return warnings
    
    def _check_pacing(self, draft: str) -> List[Dict[str, Any]]:
        """检查节奏"""
        warnings = []
        
        paragraphs = [p.strip() for p in draft.split('\n\n') if p.strip()]
        avg_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        short_paragraphs = sum(1 for p in paragraphs if len(p) < 50)
        long_paragraphs = sum(1 for p in paragraphs if len(p) > 500)
        
        if short_paragraphs / len(paragraphs) > 0.5 if paragraphs else False:
            warnings.append({
                "dimension": "pacing",
                "type": "too_many_short",
                "severity": "warning",
                "message": f"短段落过多 ({short_paragraphs}/{len(paragraphs)})",
                "suggestion": "增加中等长度段落，改善节奏"
            })
        
        if long_paragraphs / len(paragraphs) > 0.3 if paragraphs else False:
            warnings.append({
                "dimension": "pacing",
                "type": "too_many_long",
                "severity": "warning",
                "message": f"长段落过多 ({long_paragraphs}/{len(paragraphs)})",
                "suggestion": "拆分长段落，提高可读性"
            })
        
        return warnings
    
    def _check_voice(self, draft: str) -> List[Dict[str, Any]]:
        """检查文风"""
        issues = []
        
        tier1_results = self.anti_slop.detect_tier1(draft)
        for item in tier1_results:
            issues.append({
                "dimension": "voice",
                "type": "ai_word",
                "severity": "critical",
                "message": f"发现AI常用词: {item['word']}",
                "location": f"第{item['line']}行",
                "suggestion": f"替换为: {item['alternative']}"
            })
        
        not_just = self.anti_slop.detect_not_just_x_but_y(draft)
        for item in not_just[:5]:
            issues.append({
                "dimension": "voice",
                "type": "formulaic_structure",
                "severity": "warning",
                "message": "发现'不只是X，而是Y'句式",
                "suggestion": "改为更直接简洁的表达"
            })
        
        sentence_uniformity = self.anti_slop.detect_sentence_uniformity(draft)
        if sentence_uniformity.get("uniform"):
            issues.append({
                "dimension": "voice",
                "type": "uniform_sentences",
                "severity": "warning",
                "message": "句子长度过于均匀",
                "suggestion": "增加句长变化，模仿人类写作节奏"
            })
        
        return issues
    
    def _check_facts(
        self,
        draft: str,
        chapter_num: int,
        context: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检查事实一致性"""
        issues = []
        
        if not context or not context.get("canon_facts"):
            return issues
        
        for fact in context["canon_facts"][:20]:
            fact_text = fact.get("fact", "")
            if fact_text and fact_text[:30] not in draft:
                source_ch = fact.get("source_chapter", 0)
                if source_ch > 0 and chapter_num - source_ch <= 3:
                    issues.append({
                        "dimension": "fact",
                        "type": "fact_not_mentioned",
                        "severity": "warning",
                        "message": f"前文事实未在当前章提及: {fact_text[:30]}...",
                        "source": f"第{source_ch}章"
                    })
        
        return issues
    
    def _calculate_scores(self, audit_results: Dict[str, Any]) -> Dict[str, float]:
        """计算审计分数"""
        base_score = 10.0
        
        critical_issues = [i for i in audit_results["issues"] if i.get("severity") == "critical"]
        warning_issues = [i for i in audit_results["issues"] + audit_results["warnings"] 
                        if i.get("severity") == "warning"]
        
        score = base_score
        score -= len(critical_issues) * 0.5
        score -= len(warning_issues) * 0.1
        
        aigc_report = audit_results.get("aigc_report", {})
        if aigc_report:
            summary = aigc_report.get("summary", {})
            if summary.get("risk_level") == "HIGH":
                score -= 2.0
            elif summary.get("risk_level") == "MEDIUM":
                score -= 1.0
        
        return {
            "overall": max(0, score),
            "continuity": max(0, score - len([i for i in critical_issues if i["dimension"] == "continuity"]) * 0.3),
            "voice": max(0, score - len([i for i in critical_issues if i["dimension"] == "voice"]) * 0.3),
            "aigc_risk": 10 - aigc_report.get("summary", {}).get("critical_issues", 0) if aigc_report else 10
        }
    
    def _generate_recommendations(self, audit_results: Dict[str, Any]) -> List[str]:
        """生成修订建议"""
        recommendations = []
        
        for issue in audit_results["issues"]:
            if issue.get("suggestion"):
                recommendations.append(f"*{issue['dimension']}*: {issue['suggestion']}")
        
        for warning in audit_results["warnings"]:
            if warning.get("suggestion"):
                recommendations.append(f"*{warning['dimension']}*: {warning['suggestion']}")
        
        if not recommendations:
            recommendations.append("章节质量良好，建议通过。")
        
        return recommendations[:10]
    
    def quick_audit(self, draft: str) -> Dict[str, Any]:
        """
        快速审计（仅AIGC检测）
        
        Args:
            draft: 章节草稿
            
        Returns:
            简化审计报告
        """
        aigc_report = self.anti_slop.full_detect(draft)
        summary = aigc_report.get("summary", {})
        
        return {
            "pass": not summary.get("needs_revision", False),
            "risk_level": summary.get("risk_level", "UNKNOWN"),
            "critical_issues": summary.get("critical_issues", 0),
            "warning_issues": summary.get("warning_issues", 0),
            "aigc_report": aigc_report,
            "recommendations": self.anti_slop.get_revision_guidance(aigc_report)
        }
    
    def audit_full_novel(
        self,
        chapters: Dict[int, str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        全书审计
        
        Args:
            chapters: 章节字典 {章节号: 内容}
            context: 上下文
            
        Returns:
            全书审计报告
        """
        results = {
            "total_chapters": len(chapters),
            "chapter_results": {},
            "cross_chapter_issues": [],
            "overall_score": 0,
            "recommendations": []
        }
        
        for ch_num, content in sorted(chapters.items()):
            results["chapter_results"][ch_num] = self.quick_audit(content)
        
        if len(chapters) >= 2:
            prev_content = ""
            for ch_num in sorted(chapters.keys()):
                content = chapters[ch_num]
                cross_issues = self._check_cross_chapter(prev_content, content, ch_num)
                if cross_issues:
                    results["cross_chapter_issues"].extend(cross_issues)
                prev_content = content
        
        total_score = sum(r.get("overall_score", 10) for r in results["chapter_results"].values())
        results["overall_score"] = total_score / len(chapters) if chapters else 0
        
        return results
    
    def _check_cross_chapter(
        self,
        prev_content: str,
        current_content: str,
        current_chapter: int
    ) -> List[Dict[str, Any]]:
        """检查跨章问题"""
        issues = []
        
        prev_words = set(re.findall(r'[\w]{3,}', prev_content))
        current_words = set(re.findall(r'[\w]{3,}', current_content))
        
        if prev_words and current_words:
            overlap = len(prev_words & current_words) / len(prev_words)
            if overlap < 0.05:
                issues.append({
                    "chapter": current_chapter,
                    "type": "low_continuity",
                    "severity": "warning",
                    "message": f"与前章词汇重叠率过低 ({overlap:.1%})",
                    "suggestion": "检查章节过渡是否流畅"
                })
        
        return issues
