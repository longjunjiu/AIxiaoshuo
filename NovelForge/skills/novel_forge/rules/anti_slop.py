"""
反AI味规则 - AI写作特征检测与规避
参考十大经典网文风格，强调自然、真实、有个性
"""

import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class SlopWord:
    """AI词汇"""
    word: str
    tier: int
    alternative: str
    frequency_limit: int = 0


class AntiSlopRules:
    """
    反AI味规则引擎
    
    参考经典网文风格：
    - 《斗破苍穹》：爽点密集、节奏明快
    - 《凡人修仙传》：低调谨慎、不浪
    - 《诡秘之主》：悬念迭起、智斗解谜
    - 《雪中悍刀行》：文笔优美、人物立体
    - 《诛仙》：情感真实、不狗血
    """
    
    # Tier 1: 致命AI词汇 - 立即改写
    TIER1_WORDS = [
        ("delve", "dig into, look at, examine"),
        ("utilize", "use"),
        ("leverage", "use, take advantage of"),
        ("facilitate", "help, enable, make possible"),
        ("elucidate", "explain, clarify"),
        ("embark", "start, begin"),
        ("endeavor", "effort, try"),
        ("encompass", "include, cover"),
        ("multifaceted", "complex, varied"),
        ("tapestry", "describe the actual thing"),
        ("testament", "shows, proves, demonstrates"),
        ("paradigm", "model, approach, framework"),
        ("synergy", "delete and start over"),
        ("holistic", "whole, complete"),
        ("catalyze", "trigger, cause, spark"),
        ("catalyst", "trigger, cause, spark"),
        ("juxtapose", "compare, contrast, set against"),
        ("nuanced", "cut it, or show how"),
        ("realm", "area, field, domain"),
        ("landscape", "field, space, situation"),
        ("myriad", "many, lots of"),
        ("plethora", "many, a lot"),
    ]
    
    # Tier 2: 可疑词汇 - 连续出现3个以上需改写
    TIER2_WORDS = [
        "robust", "comprehensive", "seamless", "seamlessly",
        "cutting-edge", "innovative", "streamline", "empower",
        "foster", "enhance", "elevate", "optimize", "scalable",
        "pivotal", "intricate", "profound", "resonate", "underscore",
        "harness", "navigate", "cultivate", "bolster",
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
        "As we can see...",
        "As mentioned earlier...",
        "In conclusion, ...",
        "To summarize, ...",
        "Furthermore, ...",
        "Moreover, ...",
        "Additionally, ...",
        "One might argue that...",
        "It could be suggested that...",
        "This begs the question...",
        "Not just X, but Y"
    ]
    
    # 小说特定AI词汇（参考经典网文）
    FICTION_AI_TELLS = [
        "A sense of [emotion]",
        "Couldn't help but feel",
        "The weight of [abstract noun]",
        "The air was thick with [emotion/tension]",
        "Eyes widened",
        "A wave of [emotion] washed over",
        "A pang of [emotion]",
        "Heart pounded in [his/her] chest",
        "Piercing [blue/green] eyes",
        "A knowing smile"
    ]
    
    # 中文网文AI词汇
    CHINESE_AI_TELLS = [
        "眼中闪过一丝",
        "缓缓地",
        "渐渐地",
        "骤然",
        "霎时",
        "登时",
        "不由",
        "不禁",
        "心头一紧",
        "深吸一口气",
        "嘴角微微上扬",
        "脸上浮现",
        "目光深邃",
        "浑身一颤",
        "倒吸一口凉气",
        "瞳孔骤缩",
        "不可置信"
    ]
    
    # 网文经典风格词汇（好的参考）
    GOOD_NET_NOVEL_WORDS = [
        "爽", "燃", "爆", "炸",
        "憋屈", "逆袭", "打脸",
        "金手指", "系统", "外挂"
    ]
    
    # 情绪词列表
    EMOTION_WORDS = [
        "angry", "sad", "happy", "scared", "nervous", "excited",
        "jealous", "guilty", "anxious", "lonely", "desperate",
        "surprised", "confused", "disappointed", "hopeful", "proud",
        "worried", "frustrated", "relieved", "embarrassed", "grateful"
    ]
    
    def __init__(self):
        self.word_list = self._build_word_list()
    
    def _build_word_list(self) -> List[SlopWord]:
        words = []
        
        for word, alt in self.TIER1_WORDS:
            words.append(SlopWord(word, 1, alt))
        
        for word in self.TIER2_WORDS:
            words.append(SlopWord(word, 2, ""))
        
        return words
    
    def detect_tier1(self, text: str) -> List[Dict[str, Any]]:
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
    
    def detect_chinese_ai_tells(self, text: str) -> List[Dict[str, Any]]:
        """检测中文网文AI特征"""
        results = []
        
        for word in self.CHINESE_AI_TELLS:
            pattern = re.compile(re.escape(word))
            matches = list(pattern.finditer(text))
            if matches:
                results.append({
                    "word": word,
                    "count": len(matches),
                    "suggestion": "改用更具体的动作或表情描写",
                    "severity": "warning" if len(matches) < 5 else "critical"
                })
        
        return results
    
    def detect_net_novel_patterns(self, text: str) -> Dict[str, Any]:
        """检测是否符合网文经典风格"""
        patterns = {
            "has_cliffhanger": bool(re.search(r'[？！\?!\.]+$', text.strip().split('\n')[-1])),
            "has_dialogue": '"' in text or '"' in text or '「' in text or '"' in text,
            "has_action": bool(re.search(r'(打|砍|杀|踢|踹|挥|砍|劈)', text)),
            "has_emotion_show": bool(re.search(r'(攥紧|握拳|咬牙|瞪眼|后退|颤抖)', text))
        }
        
        return {
            "patterns": patterns,
            "style_score": sum(patterns.values()) / len(patterns),
            "recommendation": "增强动作描写和对话，减少叙述性语言"
        }
    
    def detect_tier2(self, text: str) -> Dict[str, Any]:
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
        word_count = len(text)
        results = {}
        
        chinese_markers = ["仿佛", "忽然", "竟然", "不禁", "宛如", "猛地", "骤然",
                          "不由", "随即", "霎时", "登时", "顿觉", "心头一紧"]
        
        for marker in chinese_markers:
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
    
    def detect_not_just_x_but_y(self, text: str) -> List[Dict[str, Any]]:
        pattern = re.compile(r'不(?:仅|只|只是)\s*[^，,]+[，,]\s*(?:而且|却是|而是)\s*[^。]+', re.UNICODE)
        matches = []
        
        for match in pattern.finditer(text):
            matches.append({
                "text": match.group(),
                "position": match.start(),
                "suggestion": "改写为更直接简洁的表达"
            })
        
        return matches
    
    def full_detect(self, text: str, word_count: int = 3000) -> Dict[str, Any]:
        return {
            "tier1_critical": self.detect_tier1(text),
            "tier2_suspicious": self.detect_tier2(text),
            "tier3_filler": self.detect_tier3(text),
            "ai_markers": self.detect_ai_markers(text, word_count),
            "chinese_ai_tells": self.detect_chinese_ai_tells(text),
            "net_novel_patterns": self.detect_net_novel_patterns(text),
            "paragraph_uniformity": self.detect_paragraph_uniformity(text),
            "sentence_uniformity": self.detect_sentence_uniformity(text),
            "not_just_x_but_y": self.detect_not_just_x_but_y(text),
            "summary": self._summarize_results(text)
        }
    
    def _summarize_results(self, text: str) -> Dict[str, Any]:
        tier1 = self.detect_tier1(text)
        tier2 = self.detect_tier2(text)
        tier3 = self.detect_tier3(text)
        markers = self.detect_ai_markers(text)
        chinese_tells = self.detect_chinese_ai_tells(text)
        
        critical_count = len(tier1) + len([t for t in chinese_tells if t.get("severity") == "critical"])
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
        guidance = ["# 反AI味修订指导\n"]
        
        tier1 = detection_result.get("tier1_critical", [])
        if tier1:
            guidance.append("## 必须改写的词汇\n")
            for item in tier1:
                guidance.append(f"- **{item['word']}** → {item['alternative']} (第{item['line']}行)")
            guidance.append("")
        
        chinese_tells = detection_result.get("chinese_ai_tells", [])
        if chinese_tells:
            guidance.append("## 中文AI特征词汇\n")
            for item in chinese_tells[:5]:
                guidance.append(f"- **{item['word']}** (出现{item['count']}次): {item['suggestion']}")
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
        
        patterns = detection_result.get("net_novel_patterns", {})
        if patterns:
            guidance.append("## 网文风格检测\n")
            guidance.append(f"- 风格得分: {patterns.get('style_score', 0):.1%}")
            guidance.append(f"- 建议: {patterns.get('recommendation', '')}")
            guidance.append("")
        
        summary = detection_result.get("summary", {})
        if summary.get("needs_revision"):
            guidance.append(f"## 总体评估\n")
            guidance.append(f"- 风险等级: {summary['risk_level']}")
            guidance.append(f"- 严重问题: {summary['critical_issues']}")
            guidance.append(f"- 警告问题: {summary['warning_issues']}")
            guidance.append("\n建议执行反检测改写模式。")
        
        return "\n".join(guidance)
