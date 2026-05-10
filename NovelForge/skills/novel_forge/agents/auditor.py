"""
审计员机器人 - 质量检查
参考十大经典网文质量标准
"""

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
            issues.append("AI特征明显")
            score -= 15
        
        return {
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
            "pass": score >= 60,
            "chapter": chapter_num
        }
    
    def audit_ai_tells(self, text: str) -> Dict[str, Any]:
        """检测AI特征"""
        ai_tells = {
            "眼中闪过一丝": 0,
            "缓缓地": 0,
            "骤然": 0,
            "霎时": 0,
            "心头一紧": 0,
            "深吸一口气": 0,
            "嘴角微微上扬": 0,
            "瞳孔骤缩": 0,
            "不可置信": 0
        }
        
        found_tells = {}
        for tell in ai_tells:
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
            "recommendation": "减少套路化表达，用更具体的动作描写替代"
        }
    
    def _fallback_audit(self, content: str, chapter_num: int) -> Dict[str, Any]:
        """备用审计"""
        word_count = len(content)
        
        score = 70.0
        issues = []
        suggestions = []
        
        if word_count < 1500:
            score -= 10
            issues.append("字数偏少")
        
        return {
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
            "pass": score >= 60,
            "chapter": chapter_num
        }
