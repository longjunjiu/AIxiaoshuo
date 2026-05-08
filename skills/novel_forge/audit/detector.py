"""
AIGC检测器 - 检测并消除AI生成特征
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from ..rules.anti_slop import AntiSlopRules


@dataclass
class DetectionResult:
    """检测结果"""
    risk_level: str  # LOW, MEDIUM, HIGH
    tier1_count: int
    tier2_clusters: int
    tier3_count: int
    marker_violations: int
    structural_issues: List[str]
    suggestions: List[str]


class AIGCDetector:
    """
    AIGC检测器
    
    提供多层次的AI内容检测：
    - 词汇层：Tier 1/2/3 AI词汇
    - 结构层：段落/句子模式
    - 统计层：困惑度/突发度
    - 语义层：内容分析
    """
    
    def __init__(self):
        self.anti_slop = AntiSlopRules()
        
        self.THRESHOLDS = {
            "tier1_critical": 0,
            "tier2_cluster": 3,
            "tier3_count": 5,
            "marker_excess": 2,
            "paragraph_uniform": 0.5,
            "sentence_uniform": 0.3
        }
    
    def detect(
        self,
        project,
        chapter_num: Optional[int] = None,
        volume_num: Optional[int] = None,
        full_novel: bool = False
    ) -> Dict[str, Any]:
        """
        检测AI内容
        
        Args:
            project: 项目实例
            chapter_num: 章节号（可选）
            volume_num: 卷号（可选）
            full_novel: 是否检测全书
            
        Returns:
            检测报告
        """
        if full_novel:
            return self._detect_full_novel(project)
        elif chapter_num:
            return self._detect_chapter(project, chapter_num, volume_num)
        else:
            return {"error": "请指定章节号或设置full_novel=True"}
    
    def _detect_chapter(
        self,
        project,
        chapter_num: int,
        volume_num: Optional[int] = None
    ) -> Dict[str, Any]:
        """检测单章"""
        vol_num = volume_num or project.current_volume
        ch = project.chapters.get(chapter_num)
        
        if not ch:
            return {"error": f"章节 {chapter_num} 不存在"}
        
        content = ch.content if hasattr(ch, 'content') else str(ch)
        
        return self._analyze_content(content, chapter_num)
    
    def _detect_full_novel(self, project) -> Dict[str, Any]:
        """检测全书"""
        results = {
            "total_chapters": len(project.chapters),
            "chapter_results": {},
            "overall_risk": "LOW",
            "hotspots": []
        }
        
        risk_levels = []
        
        for ch_num in sorted(project.chapters.keys()):
            ch = project.chapters[ch_num]
            content = ch.content if hasattr(ch, 'content') else str(ch)
            
            analysis = self._analyze_content(content, ch_num)
            results["chapter_results"][ch_num] = analysis
            
            if analysis["risk_level"] == "HIGH":
                risk_levels.append("HIGH")
                results["hotspots"].append({
                    "chapter": ch_num,
                    "type": "high_risk",
                    "issues": analysis.get("critical_issues", [])
                })
            elif analysis["risk_level"] == "MEDIUM":
                risk_levels.append("MEDIUM")
        
        if "HIGH" in risk_levels:
            results["overall_risk"] = "HIGH"
        elif "MEDIUM" in risk_levels:
            results["overall_risk"] = "MEDIUM"
        else:
            results["overall_risk"] = "LOW"
        
        results["risk_distribution"] = {
            "high": risk_levels.count("HIGH"),
            "medium": risk_levels.count("MEDIUM"),
            "low": risk_levels.count("LOW")
        }
        
        return results
    
    def _analyze_content(self, content: str, chapter: int) -> Dict[str, Any]:
        """分析内容"""
        word_count = len(content)
        
        tier1_results = self.anti_slop.detect_tier1(content)
        tier2_results = self.anti_slop.detect_tier2(content)
        tier3_results = self.anti_slop.detect_tier3(content)
        marker_results = self.anti_slop.detect_ai_markers(content)
        paragraph_results = self.anti_slop.detect_paragraph_uniformity(content)
        sentence_results = self.anti_slop.detect_sentence_uniformity(content)
        emdash_results = self.anti_slop.detect_em_dash_overuse(content)
        not_just_results = self.anti_slop.detect_not_just_x_but_y(content)
        transition_results = self.anti_slop.detect_transition_addiction(content)
        
        risk_score = self._calculate_risk_score(
            tier1_results, tier2_results, tier3_results,
            marker_results, paragraph_results, sentence_results,
            emdash_results, transition_results
        )
        
        risk_level = self._determine_risk_level(risk_score)
        
        critical_issues = self._extract_critical_issues(
            tier1_results, tier3_results, emdash_results, not_just_results
        )
        
        suggestions = self._generate_suggestions(
            tier1_results, tier2_results, tier3_results,
            marker_results, paragraph_results, sentence_results,
            transition_results
        )
        
        return {
            "chapter": chapter,
            "word_count": word_count,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "tier1_count": len(tier1_results),
            "tier2_clusters": len(tier2_results.get("clusters", [])),
            "tier3_count": len(tier3_results),
            "marker_violations": sum(1 for m in marker_results.values() if m.get("excess", 0) > 0),
            "paragraph_uniform_rate": len(paragraph_results) / max(1, len([p for p in content.split('\n\n') if p.strip()])),
            "critical_issues": critical_issues,
            "suggestions": suggestions,
            "detailed_report": {
                "tier1": tier1_results[:5],
                "tier2_clusters": tier2_results.get("clusters", [])[:3],
                "tier3_phrases": tier3_results[:5],
                "marker_excess": {k: v for k, v in marker_results.items() if v.get("excess", 0) > 0}
            }
        }
    
    def _calculate_risk_score(
        self,
        tier1: List,
        tier2: Dict,
        tier3: List,
        markers: Dict,
        paragraphs: List,
        sentences: Dict,
        emdash: Dict,
        transitions: Dict
    ) -> float:
        """计算风险分数"""
        score = 0.0
        
        score += len(tier1) * 2.0
        score += len(tier2.get("clusters", [])) * 1.5
        score += len(tier3) * 0.5
        
        marker_excess = sum(m.get("excess", 0) for m in markers.values())
        score += marker_excess * 0.3
        
        if paragraphs:
            score += len(paragraphs) * 0.5
        
        if sentences.get("uniform"):
            score += 1.0
        
        if emdash.get("severity") == "critical":
            score += 1.5
        elif emdash.get("severity") == "warning":
            score += 0.5
        
        if transitions.get("severity") == "critical":
            score += 1.5
        elif transitions.get("severity") == "warning":
            score += 0.5
        
        return score
    
    def _determine_risk_level(self, score: float) -> str:
        """确定风险等级"""
        if score >= 10:
            return "HIGH"
        elif score >= 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _extract_critical_issues(
        self,
        tier1: List,
        tier3: List,
        emdash: Dict,
        not_just: List
    ) -> List[str]:
        """提取严重问题"""
        issues = []
        
        for item in tier1[:3]:
            issues.append(f"AI词汇: {item['word']}")
        
        for item in tier3[:3]:
            issues.append(f"填充语: {item['phrase'][:30]}")
        
        if emdash.get("excess", 0) > 5:
            issues.append(f"破折号滥用: {emdash['count']}个（超过{emdash['allowed']}个限制）")
        
        if len(not_just) > 0:
            issues.append(f"'不只是X，而是Y'句式: {len(not_just)}处")
        
        return issues
    
    def _generate_suggestions(
        self,
        tier1: List,
        tier2: Dict,
        tier3: List,
        markers: Dict,
        paragraphs: List,
        sentences: Dict,
        transitions: Dict
    ) -> List[str]:
        """生成建议"""
        suggestions = []
        
        if tier1:
            suggestions.append("使用更口语化、自然的词汇替代AI词汇")
        
        if tier2.get("clusters"):
            suggestions.append("减少过度使用的正式词汇，增加变化")
        
        if tier3:
            suggestions.append("删除无意义的填充语和过渡句")
        
        if markers:
            excess_markers = [m for m, v in markers.items() if v.get("excess", 0) > 0]
            if excess_markers:
                suggestions.append(f"减少AI标记词使用: {', '.join(excess_markers)}")
        
        if paragraphs:
            suggestions.append("增加段落长度变化，避免机械均匀")
        
        if sentences.get("uniform"):
            suggestions.append("增加句子长度变化，模仿人类写作节奏")
        
        if transitions.get("ratio", 0) > 0.5:
            suggestions.append("避免每个段落都以过渡词开头")
        
        if not suggestions:
            suggestions.append("文本AI特征较少，继续保持")
        
        return suggestions[:5]
    
    def batch_detect(
        self,
        contents: List[Tuple[int, str]]
    ) -> Dict[str, Any]:
        """
        批量检测
        
        Args:
            contents: [(章节号, 内容), ...]
            
        Returns:
            批量检测报告
        """
        results = {
            "total": len(contents),
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "chapters": {}
        }
        
        for ch_num, content in contents:
            analysis = self._analyze_content(content, ch_num)
            results["chapters"][ch_num] = analysis
            
            if analysis["risk_level"] == "HIGH":
                results["high_risk"] += 1
            elif analysis["risk_level"] == "MEDIUM":
                results["medium_risk"] += 1
            else:
                results["low_risk"] += 1
        
        return results
    
    def get_statistics(self, detection_result: Dict) -> Dict[str, Any]:
        """获取统计信息"""
        chapters = detection_result.get("chapter_results", {})
        
        if not chapters:
            return {}
        
        tier1_counts = [r["tier1_count"] for r in chapters.values()]
        tier2_counts = [r["tier2_clusters"] for r in chapters.values()]
        
        return {
            "total_tier1": sum(tier1_counts),
            "avg_tier1_per_chapter": sum(tier1_counts) / len(tier1_counts) if tier1_counts else 0,
            "total_tier2_clusters": sum(tier2_counts),
            "chapters_with_issues": len([r for r in chapters.values() if r["tier1_count"] > 0]),
            "highest_risk_chapter": max(chapters.items(), key=lambda x: x[1]["risk_score"])[0] if chapters else None
        }
