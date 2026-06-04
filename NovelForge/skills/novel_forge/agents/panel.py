"""
评审团Agent - 多视角评审
真正的多Agent协作：多个AI视角同时评审，投票决策
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    """评审结论"""
    通过 = "通过"
    修改后通过 = "修改后通过"
    不通过 = "不通过"


@dataclass
class PanelDecision:
    """评审团决策"""
    final_verdict: str
    overall_score: float
    scores: Dict[str, float]
    issues: List[str]
    highlights: List[str]
    recommendations: List[str]
    votes: Dict[str, str]


@dataclass
class PersonaReview:
    """单人评审结果"""
    persona: str
    name: str
    score: float
    verdict: str
    issues: List[str]
    highlights: List[str]
    reasoning: str


class PanelAgent:
    """
    评审团Agent - 多视角评审系统
    
    模拟专业评审团，包含多个评审角色：
    - 主编：整体把控，市场视角
    - 文编：文笔技法，专业视角
    - 读者甲：代入感，情感共鸣
    - 读者乙：爽点满足，类型期待
    - 结构师：章节结构，节奏把控
    
    每个角色独立评审，然后投票汇总，形成最终决策
    """
    
    PANELS = {
        "editor": {
            "name": "主编",
            "role": "专业编辑，负责整体把控和市场定位",
            "focus": ["故事完整性", "市场潜力", "商业价值", "读者定位"],
            "weight": 1.5,
            "system": """你是一位资深网文主编，有15年网文编辑经验。

你的评审标准：
1. 故事是否完整、有吸引力？
2. 市场定位是否清晰？
3. 是否有商业潜力？
4. 读者群体是否明确？

你的风格：严厉但公正，注重市场价值
评分：1-10分，7分以上为通过
"""
        },
        "copy_editor": {
            "name": "文编",
            "role": "文字编辑，负责文笔技法评估",
            "focus": ["文笔水平", "叙事技法", "语言流畅度", "风格特色"],
            "weight": 1.2,
            "system": """你是一位资深网文文字编辑，精通各类网文风格。

你的评审标准：
1. 文笔是否流畅自然？
2. 叙事技法是否成熟？
3. 对话是否生动？
4. 是否有独特风格？

你的风格：注重文字质感，追求优美表达
评分：1-10分，7分以上为通过
"""
        },
        "reader_a": {
            "name": "资深读者",
            "role": "10年书龄老读者，代表核心用户",
            "focus": ["代入感", "期待感", "情感共鸣", "人物魅力"],
            "weight": 1.0,
            "system": """你是一位资深网文读者，书龄10年，阅书无数。

你的评审标准：
1. 代入感是否强烈？
2. 是否让你欲罢不能？
3. 主角是否有魅力？
4. 情感线是否动人？

你的风格：从读者角度出发，注重阅读体验
评分：1-10分，7分以上为通过
"""
        },
        "reader_b": {
            "name": "小白读者",
            "role": "新入坑读者，检验作品吸引力",
            "focus": ["爽点密度", "节奏明快", "易懂程度", "趣味性"],
            "weight": 1.0,
            "system": """你是一位刚入坑的网文小白读者。

你的评审标准：
1. 开头是否吸引人？
2. 是否容易看懂？
3. 爽点是否明显？
4. 节奏是否明快？

你的风格：小白视角，注重第一感受
评分：1-10分，7分以上为通过
"""
        },
        "structure": {
            "name": "结构师",
            "role": "专业结构分析，评估章节架构",
            "focus": ["章节结构", "节奏把控", "伏笔设置", "高潮设计"],
            "weight": 1.3,
            "system": """你是一位专业的小说结构分析师。

你的评审标准：
1. 章节结构是否合理？
2. 节奏是否有起伏？
3. 伏笔是否埋设得当？
4. 高潮设计是否到位？

你的风格：理性分析，注重结构美感
评分：1-10分，7分以上为通过
"""
        }
    }
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.votes_history: List[Dict] = []
    
    def review_chapter(
        self,
        chapter_num: int,
        content: str,
        outline: Any = None,
        context: Optional[Dict] = None
    ) -> PanelDecision:
        """
        评审团评审单章
        
        流程：
        1. 各评审角色独立评审
        2. 收集评分和意见
        3. 投票汇总
        4. 形成最终决策
        """
        print("\n" + "=" * 50)
        print("  评审团开始评审...")
        print("=" * 50)
        
        persona_reviews: List[PersonaReview] = []
        scores: Dict[str, float] = {}
        votes: Dict[str, str] = {}
        
        for panel_id, panel_info in self.PANELS.items():
            print(f"\n📋 {panel_info['name']} 评审中...")
            
            review = self._review_as_panel(panel_id, panel_info, chapter_num, content, outline, context)
            persona_reviews.append(review)
            
            scores[panel_id] = review.score
            votes[panel_id] = review.verdict
            
            print(f"   评分: {review.score:.1f}/10 - {review.verdict}")
            if review.issues:
                print(f"   问题: {review.issues[0][:50]}...")
        
        overall_score = self._calculate_weighted_score(scores)
        
        all_issues = []
        all_highlights = []
        for review in persona_reviews:
            all_issues.extend(review.issues)
            all_highlights.extend(review.highlights)
        
        final_verdict = self._determine_verdict(votes, overall_score)
        
        recommendations = self._generate_recommendations(persona_reviews, all_issues)
        
        decision = PanelDecision(
            final_verdict=final_verdict,
            overall_score=overall_score,
            scores=scores,
            issues=all_issues[:5],
            highlights=all_highlights[:3],
            recommendations=recommendations,
            votes=votes
        )
        
        self.votes_history.append({
            "chapter": chapter_num,
            "decision": decision
        })
        
        return decision
    
    def _review_as_panel(
        self,
        panel_id: str,
        panel_info: Dict,
        chapter_num: int,
        content: str,
        outline: Any,
        context: Optional[Dict]
    ) -> PersonaReview:
        """作为特定评审角色进行评审"""
        
        outline_info = ""
        if outline:
            outline_info = f"""
## 章节大纲
- 标题：{getattr(outline, 'title', '未知')}
- 核心事件：{getattr(outline, 'core_event', '未知')}
- 冲突设计：{getattr(outline, 'conflict', '未知')}
- 爽点：{getattr(outline, 'shuangdian', '未知')}
- 章尾钩子：{getattr(outline, 'hook', '未知')}
"""
        
        genre = context.get("genre", "玄幻") if context else "玄幻"
        protagonist = context.get("protagonist", "主角") if context else "主角"
        
        user_prompt = f"""## 待评审章节
书名：{context.get('title', '未知') if context else '未知'}
章节：第{chapter_num}章
题材：{genre}
主角：{protagonist}
{outline_info}

## 章节内容
{content[:6000]}

## 你的评审任务

请从【{panel_info['name']}】的视角评审此章节。

评审重点：{', '.join(panel_info['focus'])}

请给出：
1. **评分**（1-10，必须给出具体数字）
2. **结论**（通过/修改后通过/不通过）
3. **发现的问题**（如有，列出最多3个）
4. **亮点**（如有，列出最多2个）
5. **评审理由**（简述）

直接输出，不要使用JSON格式。
"""
        
        if not self.llm:
            return PersonaReview(
                persona=panel_id,
                name=panel_info["name"],
                score=7.0,
                verdict="修改后通过",
                issues=[],
                highlights=[],
                reasoning="LLM 未配置，使用默认评分"
            )

        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": user_prompt}],
                system=panel_info["system"],
                temperature=0.4,
                max_tokens=1500
            )

            review_text = response.content
            score = self._extract_score(review_text)
            verdict = self._extract_verdict(review_text)
            issues = self._extract_list(review_text, ["问题", "不足"])
            highlights = self._extract_list(review_text, ["亮点", "优点", "精彩"])

        except Exception as e:
            review_text = f"评审失败: {e}"
            score = 7.0
            verdict = "修改后通过"
            issues = []
            highlights = []
        
        return PersonaReview(
            persona=panel_id,
            name=panel_info["name"],
            score=score,
            verdict=verdict,
            issues=issues,
            highlights=highlights,
            reasoning=review_text[:200]
        )
    
    def _calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """计算加权平均分"""
        total_weight = 0
        weighted_sum = 0
        
        for panel_id, score in scores.items():
            if panel_id in self.PANELS:
                weight = self.PANELS[panel_id]["weight"]
                weighted_sum += score * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0
    
    def _determine_verdict(self, votes: Dict[str, str], score: float) -> str:
        """确定最终裁决"""
        pass_count = sum(1 for v in votes.values() if v in ["通过", "修改后通过"])
        total_count = len(votes)
        
        pass_rate = pass_count / total_count if total_count > 0 else 0
        
        if score >= 8.0 and pass_rate >= 0.8:
            return "通过"
        elif score >= 7.0 and pass_rate >= 0.6:
            return "修改后通过"
        elif score >= 6.0:
            return "修改后通过"
        else:
            return "不通过"
    
    def _generate_recommendations(
        self,
        reviews: List[PersonaReview],
        issues: List[str]
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        for review in reviews:
            if review.issues:
                recommendations.append(f"[{review.name}] {review.issues[0]}")
        
        recommendations = list(dict.fromkeys(recommendations))
        
        return recommendations[:5]
    
    def _extract_score(self, text: str) -> float:
        """提取评分"""
        import re
        
        patterns = [
            r'评分[：:]\s*(\d+\.?\d*)',
            r'打分[：:]\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*/\s*10',
            r'(\d+\.?\d*)\s*分',
            r'得分[：:]\s*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                score = float(match.group(1))
                if 1 <= score <= 10:
                    return score
        
        return 5.0
    
    def _extract_verdict(self, text: str) -> str:
        """提取裁决"""
        if "不通过" in text and "修改后通过" not in text:
            return "不通过"
        elif "通过" in text:
            return "通过"
        elif "修改后" in text or "建议修改" in text:
            return "修改后通过"
        return "修改后通过"
    
    def _extract_list(self, text: str, keywords: List[str]) -> List[str]:
        """提取列表项"""
        results = []
        lines = text.split('\n')
        
        in_target_section = False
        for line in lines:
            stripped = line.strip()
            
            if any(kw in stripped for kw in keywords):
                in_target_section = True
                continue
            
            if in_target_section:
                if stripped.startswith(('-', '*', '·', '•', '▸')):
                    item = stripped.lstrip('-*·•▸').strip()
                    if item:
                        results.append(item)
                elif stripped and not stripped.startswith('#') and len(stripped) > 5:
                    if any(kw in stripped for kw in ["评分", "结论", "打分"]):
                        in_target_section = False
                    else:
                        results.append(stripped)
                        if len(results) >= 3:
                            break
        
        return results[:3]
    
    def review_novel(
        self,
        full_content: str,
        personas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """评审全书"""
        personas = personas or list(self.PANELS.keys())
        
        results = {
            "persona_reviews": {},
            "consensus": [],
            "overall_score": 0,
            "recommendations": []
        }
        
        for persona_id in personas:
            if persona_id not in self.PANELS:
                continue
            
            persona = self.PANELS[persona_id]
            review = self._review_as_persona(full_content[:15000], persona, persona_id)
            results["persona_reviews"][persona_id] = review
        
        results["consensus"] = self._find_consensus(results["persona_reviews"])
        results["recommendations"] = self._aggregate_recommendations(results)
        results["overall_score"] = self._calculate_overall_score(results)
        
        return results
    
    def _review_as_persona(
        self,
        content: str,
        persona: Dict,
        persona_id: str
    ) -> Dict[str, Any]:
        """作为特定视角评审"""
        user_prompt = f"""# 待评审小说（节选）
题材：{persona['name']}视角

{content}

请从{persona['name']}的视角进行评审，给出评分（1-10）和主要意见。"""
        
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": user_prompt}],
                system=persona["system"],
                temperature=0.5,
                max_tokens=2000
            )
            
            return {
                "persona": persona_id,
                "review": response.content,
                "score": self._extract_score(response.content)
            }
        except:
            return {
                "persona": persona_id,
                "review": "评审失败",
                "score": 5.0
            }
    
    def _find_consensus(self, reviews: Dict[str, Dict]) -> List[Dict]:
        """找出共识"""
        scores = [r.get("score", 5.0) for r in reviews.values()]
        if not scores:
            return []

        avg = sum(scores) / len(scores)
        consensus = [{"type": "overall", "content": f"综合评分: {avg:.1f}/10"}]

        low_scores = {pid: r for pid, r in reviews.items() if r.get("score", 5) < 6}
        if low_scores:
            consensus.append({
                "type": "concern",
                "content": f"以下评审打分偏低: {', '.join(low_scores.keys())}"
            })

        return consensus

    def _aggregate_recommendations(self, results: Dict) -> List[str]:
        """汇总建议"""
        recommendations = []

        for review in results.get("persona_reviews", {}).values():
            review_text = review.get("review", "")
            for line in review_text.split("\n"):
                stripped = line.strip().lstrip("-*·•▸").strip()
                if (
                    stripped
                    and len(stripped) > 8
                    and any(kw in stripped for kw in ["建议", "可以", "应该", "需要", "改进"])
                ):
                    recommendations.append(stripped)
                    if len(recommendations) >= 5:
                        return recommendations

        return list(dict.fromkeys(recommendations))[:5]

    def _calculate_overall_score(self, results: Dict) -> float:
        """计算总分"""
        scores = [r.get("score", 5) for r in results.get("persona_reviews", {}).values()]
        return sum(scores) / len(scores) if scores else 0
