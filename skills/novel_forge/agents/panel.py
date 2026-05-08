"""
评审团Agent - 多视角评审
"""

from typing import Dict, List, Optional, Any


class PanelAgent:
    """
    评审团Agent
    
    模拟多个视角对小说进行评审：
    - 编辑视角：整体结构和节奏
    - 类型读者视角：爽点满足
    - 写手视角：技法评估
    - 普通读者视角：阅读体验
    """
    
    PERSONAS = {
        "editor": {
            "name": "资深编辑",
            "focus": ["结构", "节奏", "市场"],
            "questions": [
                "故事结构是否完整？",
                "节奏是否有起伏？",
                "是否有市场潜力？"
            ]
        },
        "genre_reader": {
            "name": "类型读者",
            "focus": ["爽点", "期待感", "代入感"],
            "questions": [
                "爽点是否到位？",
                "是否满足类型期待？",
                "是否容易代入？"
            ]
        },
        "writer": {
            "name": "同行写手",
            "focus": ["技法", "文笔", "创新"],
            "questions": [
                "写作技法是否成熟？",
                "是否有独特风格？",
                "是否有创新之处？"
            ]
        },
        "casual_reader": {
            "name": "普通读者",
            "focus": ["可读性", "趣味性", "情感共鸣"],
            "questions": [
                "是否容易阅读？",
                "是否有趣味？",
                "是否引发情感共鸣？"
            ]
        }
    }
    
    def __init__(self, llm_client, project):
        self.llm = llm_client
        self.project = project
    
    def review_novel(
        self,
        full_content: str,
        personas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        评审全书
        
        Args:
            full_content: 全书内容
            personas: 使用的评审视角列表
            
        Returns:
            评审报告
        """
        personas = personas or list(self.PERSONAS.keys())
        
        results = {
            "persona_reviews": {},
            "consensus": [],
            "overall_score": 0,
            "recommendations": []
        }
        
        for persona_id in personas:
            if persona_id not in self.PERSONAS:
                continue
            
            persona = self.PERSONAS[persona_id]
            review = self._review_as_persona(full_content, persona, persona_id)
            results["persona_reviews"][persona_id] = review
        
        results["consensus"] = self._find_consensus(results["persona_reviews"])
        results["recommendations"] = self._aggregate_recommendations(results)
        results["overall_score"] = self._calculate_overall_score(results)
        
        return results
    
    def review_chapter(
        self,
        chapter_content: str,
        chapter_num: int,
        personas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        评审单章
        
        Args:
            chapter_content: 章节内容
            chapter_num: 章节号
            personas: 评审视角
            
        Returns:
            评审报告
        """
        personas = personas or ["editor", "genre_reader"]
        
        results = {
            "chapter": chapter_num,
            "persona_reviews": {},
            "issues": [],
            "highlights": [],
            "score": 0
        }
        
        for persona_id in personas:
            if persona_id not in self.PERSONAS:
                continue
            
            persona = self.PERSONAS[persona_id]
            review = self._review_chapter_as_persona(
                chapter_content, chapter_num, persona, persona_id
            )
            results["persona_reviews"][persona_id] = review
            
            if review.get("issues"):
                results["issues"].extend(review["issues"])
            if review.get("highlights"):
                results["highlights"].extend(review["highlights"])
        
        results["score"] = sum(
            r.get("score", 5) for r in results["persona_reviews"].values()
        ) / len(results["persona_reviews"]) if results["persona_reviews"] else 0
        
        return results
    
    def _review_as_persona(
        self,
        content: str,
        persona: Dict,
        persona_id: str
    ) -> Dict[str, Any]:
        """作为特定视角评审"""
        system_prompt = f"""你是一位{persona['name']}，负责评审网络小说。

评审重点：
- {' / '.join(persona['focus'])}

请仔细阅读小说内容，给出：
1. 总体评价（1-10分）
2. 主要优点
3. 主要问题
4. 改进建议

注意：
- 保持客观公正
- 给出具体可行的建议
- 考虑目标读者群体

直接输出评审内容，不要使用JSON格式。"""
        
        sample = content[:10000]
        
        user_prompt = f"""# 待评审小说
书名：{self.project.title}
题材：{self.project.genre}

{sample}

请从{persona['name']}的视角进行评审。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.5,
            max_tokens=3000
        )
        
        return {
            "persona": persona_id,
            "review": response.content,
            "score": self._extract_score(response.content),
            "issues": self._extract_issues(response.content),
            "highlights": self._extract_highlights(response.content)
        }
    
    def _review_chapter_as_persona(
        self,
        content: str,
        chapter_num: int,
        persona: Dict,
        persona_id: str
    ) -> Dict[str, Any]:
        """作为特定视角评审单章"""
        system_prompt = f"""你是一位{persona['name']}，负责评审网络小说章节。

评审重点：
- {' / '.join(persona['focus'])}

请评审指定章节，给出：
1. 评分（1-10）
2. 亮点
3. 问题（如有）
4. 建议（如有）

直接输出评审内容。"""
        
        user_prompt = f"""# 待评审章节
书名：{self.project.title}
章节：第{chapter_num}章

{content[:5000]}

请从{persona['name']}的视角评审此章节。"""
        
        response = self.llm.chat(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            temperature=0.5,
            max_tokens=2000
        )
        
        return {
            "persona": persona_id,
            "review": response.content,
            "score": self._extract_score(response.content),
            "issues": self._extract_issues(response.content),
            "highlights": self._extract_highlights(response.content)
        }
    
    def _find_consensus(self, reviews: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """找出共识问题"""
        all_issues = []
        
        for review in reviews.values():
            for issue in review.get("issues", []):
                all_issues.append(issue)
        
        consensus = []
        issue_counts = {}
        
        for issue in all_issues:
            key = issue[:30]
            issue_counts[key] = issue_counts.get(key, 0) + 1
        
        for issue, count in issue_counts.items():
            if count >= 2:
                consensus.append({
                    "issue": issue,
                    "agreement_count": count,
                    "severity": "high" if count >= 3 else "medium"
                })
        
        return consensus
    
    def _aggregate_recommendations(self, results: Dict) -> List[str]:
        """汇总建议"""
        recommendations = []
        
        for review in results.get("persona_reviews", {}).values():
            review_text = review.get("review", "")
            lines = review_text.split('\n')
            
            for line in lines:
                if '建议' in line or '改进' in line:
                    recommendations.append(line.strip())
        
        return list(dict.fromkeys(recommendations))[:10]
    
    def _calculate_overall_score(self, results: Dict) -> float:
        """计算总分"""
        scores = [
            r.get("score", 5)
            for r in results.get("persona_reviews", {}).values()
        ]
        
        return sum(scores) / len(scores) if scores else 0
    
    def _extract_score(self, text: str) -> float:
        """提取评分"""
        import re
        
        patterns = [
            r'评分[：:]\s*(\d+\.?\d*)',
            r'打分[：:]\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*/\s*10',
            r'(\d+\.?\d*)\s*分'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1))
        
        return 5.0
    
    def _extract_issues(self, text: str) -> List[str]:
        """提取问题"""
        issues = []
        lines = text.split('\n')
        
        in_issues_section = False
        for line in lines:
            if '问题' in line:
                in_issues_section = True
                continue
            if '优点' in line or '亮点' in line:
                in_issues_section = False
            
            if in_issues_section and line.strip().startswith(('-', '*', '·', '•')):
                issues.append(line.strip()[1:].strip())
        
        return issues
    
    def _extract_highlights(self, text: str) -> List[str]:
        """提取亮点"""
        highlights = []
        lines = text.split('\n')
        
        in_highlight_section = False
        for line in lines:
            if '优点' in line or '亮点' in line:
                in_highlight_section = True
                continue
            if '问题' in line:
                in_highlight_section = False
            
            if in_highlight_section and line.strip().startswith(('-', '*', '·', '•')):
                highlights.append(line.strip()[1:].strip())
        
        return highlights
