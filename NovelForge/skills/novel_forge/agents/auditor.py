"""
审计员机器人 - 质量检查
参考十大经典网文质量标准
"""

import json
import re
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class AuditResult:
    """审计结果"""
    score: float
    issues: List[str]
    suggestions: List[str]
    passed: bool


class AuditorAgent:
    """审计员机器人"""

    AI_TELLS = [
        "眼中闪过一丝", "缓缓地", "骤然", "霎时", "心头一紧",
        "深吸一口气", "嘴角微微上扬", "瞳孔骤缩", "不可置信",
        "浑身一颤", "目光深邃", "脸上浮现", "倒吸一口凉气",
        "嘴角勾起", "眼神复杂", "心中一动"
    ]

    def __init__(self, llm_client=None, project=None, anti_slop=None):
        self.llm = llm_client
        self.project = project
        self.anti_slop = anti_slop

    def get_system_prompt(self) -> str:
        return """你是一位顶尖网络小说质量审计师，精通网文质量标准。

【审计维度】

1. 剧情逻辑（30分）
   - 情节发展是否合理
   - 人物行为是否自洽
   - 冲突解决是否有逻辑

2. 节奏把控（25分）
   - 开局是否抓人
   - 中段是否拖沓
   - 高潮是否到位

3. 人物塑造（20分）
   - 主角是否有魅力
   - 配角是否立体
   - 对话是否自然

4. 文字质量（15分）
   - 语句是否通顺
   - 描写是否生动
   - 有无错别字

5. 爽点设计（10分）
   - 是否有爽点
   - 爽点密度

总分：100分，及格线：60分

请严格按照以上标准进行审计。"""

    def audit_chapter(
        self,
        chapter_num: int = 1,
        draft: str = "",
        context: Dict = None
    ) -> Dict[str, Any]:
        """审计章节质量"""
        if not draft:
            return self._fallback_audit("（空内容）", chapter_num)

        issues = []
        suggestions = []
        score = 70.0

        if len(draft) < 1500:
            issues.append("字数偏少，建议2000-3000字")
            score -= 10

        ai_check = self.audit_ai_tells(draft)
        if ai_check["severity"] == "high":
            issues.append(f"AI特征明显，发现{len(ai_check['found_tells'])}个AI词汇")
            score -= 15
        elif ai_check["severity"] == "medium":
            issues.append("存在一定AI特征，建议润色")
            score -= 5

        # Use LLM for detailed audit when available
        if self.llm:
            try:
                llm_result = self._audit_with_llm(chapter_num, draft, context)
                llm_score = llm_result.get('score', 0)
                if llm_score > 0:
                    score = (score + llm_score * 10) / 2
                issues.extend(llm_result.get('issues', []))
                suggestions.extend(llm_result.get('suggestions', []))
            except Exception:
                pass

        if not suggestions:
            if ai_check["found_tells"]:
                suggestions.append(f"替换AI词汇: {list(ai_check['found_tells'].keys())[:3]}")
            if len(draft) < 2000:
                suggestions.append("增加字数，丰富场景描写和对话")

        return {
            "score": max(0.0, min(100.0, score)),
            "issues": issues[:5],
            "suggestions": suggestions[:5],
            "pass": score >= 60,
            "chapter": chapter_num,
            "ai_tells": ai_check,
            "word_count": len(draft)
        }

    def _audit_with_llm(self, chapter_num: int, draft: str, context: Dict = None) -> Dict[str, Any]:
        """使用LLM进行深度审计"""
        prompt = f"""请对以下小说章节进行质量审计：

章节号：第{chapter_num}章
字数：约{len(draft)}字

章节内容（节选）：
{draft[:4000]}

请从以下5个维度评审，并以JSON格式输出结果：
```json
{{
    "score": 综合评分(1-10的浮点数),
    "plot_logic": "剧情逻辑评价（一句话）",
    "pacing": "节奏评价（一句话）",
    "character": "人物塑造评价（一句话）",
    "language": "文字质量评价（一句话）",
    "shuangdian": "爽点设计评价（一句话）",
    "issues": ["最关键的问题1", "问题2（如有）"],
    "suggestions": ["最重要改进建议1", "建议2（如有）"]
}}
```"""

        response = self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.get_system_prompt(),
            temperature=0.3,
            max_tokens=1000
        )

        json_match = re.search(r'```json\s*(.*?)\s*```', response.content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        return {}

    def audit_ai_tells(self, text: str) -> Dict[str, Any]:
        """检测AI特征词汇"""
        found_tells = {}
        for tell in self.AI_TELLS:
            count = text.count(tell)
            if count > 0:
                found_tells[tell] = count

        severity = "low"
        if len(found_tells) > 3:
            severity = "medium"
        if len(found_tells) > 5:
            severity = "high"

        return {
            "found_tells": found_tells,
            "severity": severity,
            "recommendation": "用更具体的动作描写替代套路化表达"
        }

    def _fallback_audit(self, content: str, chapter_num: int) -> Dict[str, Any]:
        """基础审计（无内容时）"""
        return {
            "score": 0.0,
            "issues": ["章节内容为空"],
            "suggestions": ["请先生成章节内容"],
            "pass": False,
            "chapter": chapter_num,
            "word_count": 0
        }
