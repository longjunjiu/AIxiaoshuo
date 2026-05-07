"""
反AI味规则 - AI写作特征检测与规避
整合自 autonovel 的 ANTI-SLOP.md
"""

import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class SlopWord:
    """AI词汇"""
    word: str
    tier: int  # 1=致命, 2=可疑, 3=填充
    alternative: str
    frequency_limit: int = 0  # 每n字允许出现1次


class AntiSlopRules:
    """
    反AI味规则引擎
    
    提供AI写作特征词汇表和检测规则，帮助生成更有人味的文字
    """
    
    # Tier 1: 致命AI词汇 - 立即改写
    TIER1_WORDS = [
        ("delve", "dig into, look at, examine"),
        ("utilize", "use"),
        ("leverage", "use, take advantage of"),
        ("leverage (verb)", "use"),
        ("facilitate", "help, enable, make possible"),
        ("elucidate", "explain, clarify"),
        ("embark", "start, begin"),
        ("endeavor", "effort, try"),
        ("encompass", "include, cover"),
        ("multifaceted", "complex, varied"),
        ("tapestry", "describe the actual thing instead"),
        ("testament", "shows, proves, demonstrates"),
        ("paradigm", "model, approach, framework"),
        ("synergy", "delete and start over"),
        ("holistic", "whole, complete, full-picture"),
        ("catalyze", "trigger, cause, spark"),
        ("catalyst", "trigger, cause, spark"),
        ("juxtapose", "compare, contrast, set against"),
        ("nuanced (as filler)", "cut it, or show how"),
        ("realm", "area, field, domain"),
        ("landscape (metaphorical)", "field, space, situation"),
        ("tapestry of", "always delete"),
        ("myriad", "many, lots of"),
        ("plethora", "many, a lot"),
    ]
    
    # Tier 2: 可疑词汇 - 连续出现3个以上需改写
    TIER2_WORDS = [
        "robust", "comprehensive", "seamless", "seamlessly",
        "cutting-edge", "innovative", "streamline", "empower",
        "foster", "enhance", "elevate", "optimize", "scalable",
        "pivotal", "intricate", "profound", "resonate", "underscore",
        "harness", "navigate (metaphorical)", "cultivate", "bolster",
        "galvanize", "cornerstone", "game-changer"
    ]
    
    # Tier 3: 填充短语 - 无信息量，删除
    TIER3_PHRASES = [
        "It's worth noting that...",
        "It's important to note that...",
        "Importantly, ...",
        "Notably, ...",
        "Interestingly, ...",
        "Let's dive into...",
        "Let's explore...",
        "In this section, we will...",
        "As we can see...",
        "As mentioned earlier...",
        "In conclusion, ...",
        "To summarize, ...",
        "Furthermore, ...",
        "Moreover, ...",
        "Additionally, ...",
        "In today's [fast-paced/digital/modern] world...",
        "At the end of the day...",
        "It goes without saying...",
        "Without further ado...",
        "When it comes to...",
        "In the realm of...",
        "One might argue that...",
        "It could be suggested that...",
        "This begs the question...",
        "A [comprehensive/holistic/nuanced] approach to...",
        "Not just X, but Y"
    ]
    
    # 小说特定AI词汇（来自CRAFT.md）
    FICTION_AI_TELLS = [
        "A sense of [emotion]",
        "Couldn't help but feel",
        "The weight of [abstract noun]",
        "The air was thick with [emotion/tension]",
        "Eyes widened",
        "A wave of [emotion] washed over",
        "A pang of [emotion]",
        "Heart pounded in [his/her] chest",
        "[Raven/dark/golden] hair [spilled/cascaded/tumbled]",
        "Piercing [blue/green] eyes",
        "A knowing smile"
    ]
    
    # 情绪词列表（展示>讲述规则）
    EMOTION_WORDS = [
        "angry", "sad", "happy", "scared", "nervous", "excited",
        "jealous", "guilty", "anxious", "lonely", "desperate",
        "surprised", "confused", "disappointed", "hopeful", "proud",
        "worried", "frustrated", "relieved", "embarrassed", "grateful"
    ]
    
    # AI标记词（用于限频检测）
    AI_MARKER_WORDS = [
        "仿佛", "忽然", "竟然", "不禁", "宛如", "猛地", "骤然",
        "不由", "随即", "霎时", "登时", "顿觉", "心头一紧"
    ]
    
    # 无意义的开头词
    MEANINGLESS_STARTS = [
        "然而", "但是", "不过", "然而", "与此同时", "就在这时",
        "突然", "忽然", "就在此时", "只见", "但见"
    ]
    
    def __init__(self):
        self.word_list = self._build_word_list()
    
    def _build_word_list(self) -> List[SlopWord]:
        """构建词汇列表"""
        words = []
        
        for word, alt in self.TIER1_WORDS:
            words.append(SlopWord(word, 1, alt))
        
        for word in self.TIER2_WORDS:
            words.append(SlopWord(word, 2, ""))
        
        return words
    
    def detect_tier1(self, text: str) -> List[Dict[str, Any]]:
        """
        检测Tier 1致命词汇
        
        Returns:
            匹配列表 [{"word": "...", "position": n, "line": n}]
        """
        results = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            for word, alt in self.TIER1_WORDS:
                pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                matches = pattern.finditer(line)
                for match in matches:
                    results.append({
                        "word": match.group(),
                        "position": match.start(),
                        "line": line_num + 1,
                        "alternative": alt,
                        "severity": "critical"
                    })
        
        return results
    
    def detect_tier2(self, text: str) -> Dict[str, Any]:
        """
        检测Tier 2可疑词汇
        
        Returns:
            {"clusters": [list of paragraphs with 3+ tier2 words], "total_count": n}
        """
        paragraphs = text.split('\n\n')
        clusters = []
        
        for para_num, para in enumerate(paragraphs):
            matches = []
            for word in self.TIER2_WORDS:
                if re.search(r'\b' + word + r'\b', para, re.IGNORECASE):
                    matches.append(word)
            
            if len(matches) >= 3:
                clusters.append({
                    "paragraph": para_num,
                    "words": matches,
                    "text": para[:200] + "..." if len(para) > 200 else para
                })
        
        return {
            "clusters": clusters,
            "total_count": sum(len(c["words"]) for c in clusters)
        }
    
    def detect_tier3(self, text: str) -> List[Dict[str, Any]]:
        """
        检测Tier 3填充短语
        
        Returns:
            匹配列表
        """
        results = []
        
        for phrase in self.TIER3_PHRASES:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            matches = pattern.finditer(text)
            for match in matches:
                results.append({
                    "phrase": match.group(),
                    "position": match.start(),
                    "suggestion": "删除此填充语"
                })
        
        return results
    
    def detect_ai_markers(self, text: str, per_words: int = 3000) -> Dict[str, Any]:
        """
        检测AI标记词频率
        
        Args:
            text: 文本
            per_words: 每多少字允许出现1次
            
        Returns:
            检测结果
        """
        word_count = len(text)
        results = {}
        
        for marker in self.AI_MARKER_WORDS:
            count = text.count(marker)
            allowed = word_count // per_words
            if count > allowed:
                results[marker] = {
                    "count": count,
                    "allowed": max(1, allowed),
                    "excess": count - max(1, allowed),
                    "severity": "warning" if count <= allowed * 2 else "critical"
                }
        
        return results
    
    def detect_paragraph_uniformity(self, text: str, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        检测段落等长问题
        
        AI倾向于生成等长的段落，这是个明显特征
        
        Returns:
            可能存在问题的段落列表
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if len(paragraphs) < 3:
            return []
        
        lengths = [len(p) for p in paragraphs]
        avg_length = sum(lengths) / len(lengths)
        
        results = []
        for i, (para, length) in enumerate(zip(paragraphs, lengths)):
            deviation = abs(length - avg_length) / avg_length if avg_length > 0 else 0
            if deviation < threshold:
                results.append({
                    "paragraph": i,
                    "length": length,
                    "avg_length": avg_length,
                    "deviation": deviation,
                    "severity": "warning"
                })
        
        return results
    
    def detect_sentence_uniformity(self, text: str) -> Dict[str, Any]:
        """
        检测句子长度均匀性问题
        
        AI句子长度往往过于均匀，缺乏人类写作的自然变化
        
        Returns:
            检测结果
        """
        import re
        sentences = re.split(r'[。！？.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 5:
            return {"uniform": False, "reason": "句子数量不足"}
        
        lengths = [len(s) for s in sentences]
        
        mean_length = sum(lengths) / len(lengths)
        variance = sum((l - mean_length) ** 2 for l in lengths) / len(lengths)
        std_dev = variance ** 0.5
        coefficient_of_variation = std_dev / mean_length if mean_length > 0 else 0
        
        is_uniform = coefficient_of_variation < 0.3
        
        return {
            "uniform": is_uniform,
            "mean_length": mean_length,
            "std_dev": std_dev,
            "coefficient_of_variation": coefficient_of_variation,
            "severity": "warning" if is_uniform else "normal"
        }
    
    def detect_em_dash_overuse(self, text: str, per_page: int = 2) -> Dict[str, Any]:
        """
        检测破折号滥用
        
        AI倾向于过度使用破折号
        
        Returns:
            检测结果
        """
        em_dashes = text.count('——') + text.count('--')
        paragraphs = text.split('\n\n')
        estimated_pages = max(1, len(paragraphs) // 3)
        
        allowed = per_page * estimated_pages
        overuse = em_dashes - allowed
        
        return {
            "count": em_dashes,
            "allowed": allowed,
            "excess": max(0, overuse),
            "severity": "critical" if overuse > 10 else "warning" if overuse > 0 else "normal"
        }
    
    def detect_not_just_x_but_y(self, text: str) -> List[Dict[str, Any]]:
        """
        检测"不只是X，而是Y"句式
        
        这是AI最常用的修辞模式
        
        Returns:
            匹配列表
        """
        pattern = re.compile(r'不(?:仅|只|只是)\s*[^，,]+[，,]\s*(?:而且|却是|而是)\s*[^。]+', re.UNICODE)
        matches = []
        
        for match in pattern.finditer(text):
            matches.append({
                "text": match.group(),
                "position": match.start(),
                "suggestion": "改写为更直接简洁的表达"
            })
        
        return matches
    
    def detect_transition_addiction(self, text: str) -> Dict[str, Any]:
        """
        检测段落开头过渡词成瘾
        
        AI每个段落都以过渡词开头
        
        Returns:
            检测结果
        """
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        transition_starts = 0
        total_starts = len(paragraphs)
        
        transition_words = [
            "然而", "但是", "不过", "而且", "此外", "同时", "因此",
            "于是", "所以", "不过", "接着", "随后", "随后", "尽管",
            "虽然", "即使", "若是", "如果", "因为", "由于", "为了",
            "尽管如此", "即便如此", "与此同时"
        ]
        
        for para in paragraphs:
            first_words = para[:10].strip()
            for tw in transition_words:
                if first_words.startswith(tw):
                    transition_starts += 1
                    break
        
        ratio = transition_starts / total_starts if total_starts > 0 else 0
        
        return {
            "transition_starts": transition_starts,
            "total_paragraphs": total_starts,
            "ratio": ratio,
            "severity": "critical" if ratio > 0.7 else "warning" if ratio > 0.5 else "normal"
        }
    
    def full_detect(self, text: str, word_count: int = 3000) -> Dict[str, Any]:
        """
        完整AI检测
        
        Returns:
            完整检测报告
        """
        return {
            "tier1_critical": self.detect_tier1(text),
            "tier2_suspicious": self.detect_tier2(text),
            "tier3_filler": self.detect_tier3(text),
            "ai_markers": self.detect_ai_markers(text, word_count),
            "paragraph_uniformity": self.detect_paragraph_uniformity(text),
            "sentence_uniformity": self.detect_sentence_uniformity(text),
            "em_dash_overuse": self.detect_em_dash_overuse(text),
            "not_just_x_but_y": self.detect_not_just_x_but_y(text),
            "transition_addiction": self.detect_transition_addiction(text),
            "summary": self._summarize_results(text)
        }
    
    def _summarize_results(self, text: str) -> Dict[str, Any]:
        """汇总检测结果"""
        tier1 = self.detect_tier1(text)
        tier2 = self.detect_tier2(text)
        tier3 = self.detect_tier3(text)
        markers = self.detect_ai_markers(text)
        
        critical_count = len(tier1)
        warning_count = len(tier2["clusters"]) + len([m for m in markers.values() if m.get("severity") == "warning"])
        
        if critical_count > 5:
            risk_level = "HIGH"
        elif critical_count > 0 or warning_count > 3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_level": risk_level,
            "critical_issues": critical_count,
            "warning_issues": warning_count,
            "needs_revision": critical_count > 0 or warning_count > 2
        }
    
    def get_revision_guidance(self, detection_result: Dict[str, Any]) -> str:
        """
        根据检测结果生成修订指导
        
        Args:
            detection_result: full_detect的返回结果
            
        Returns:
            修订指导文本
        """
        guidance = ["# 反AI味修订指导\n"]
        
        tier1 = detection_result.get("tier1_critical", [])
        if tier1:
            guidance.append("## 必须改写的词汇\n")
            for item in tier1:
                guidance.append(f"- **{item['word']}** → {item['alternative']} (第{item['line']}行)")
            guidance.append("")
        
        tier3 = detection_result.get("tier3_filler", [])
        if tier3:
            guidance.append("## 需要删除的填充语\n")
            for item in tier3[:10]:
                guidance.append(f"- `{item['phrase']}`")
            guidance.append("")
        
        not_just = detection_result.get("not_just_x_but_y", [])
        if not_just:
            guidance.append("## 句式问题\n")
            guidance.append(f"发现 {len(not_just)} 处 '不只是X，而是Y' 句式，建议改写为更直接简洁的表达。")
            guidance.append("")
        
        summary = detection_result.get("summary", {})
        if summary.get("needs_revision"):
            guidance.append(f"## 总体评估\n")
            guidance.append(f"- 风险等级: {summary['risk_level']}")
            guidance.append(f"- 严重问题: {summary['critical_issues']}")
            guidance.append(f"- 警告问题: {summary['warning_issues']}")
            guidance.append("\n建议执行反检测改写模式。")
        
        return "\n".join(guidance)
