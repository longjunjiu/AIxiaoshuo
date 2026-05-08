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
    """
    审计员机器人
    
    参考十大经典网文质量标准：
    - 《斗破苍穹》- 节奏紧凑、爽点密集
    - 《凡人修仙传》- 细节严谨、逻辑自洽
    - 《诡秘之主》- 伏笔回收、悬念迭起
    - 《雪中悍刀行》- 文笔优美、人物立体
    - 《诛仙》- 情感真挚、情节感人
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def get_system_prompt(self) -> str:
        return """你是一位顶尖网络小说质量审计师，精通网文质量标准。

【十大经典网文质量标准】

《斗破苍穹》标准：
- 节奏：紧凑明快，每章有冲突
- 爽点：密集，打脸干脆
- 升级：清晰，读者能看懂
- 核心：憋屈到位，爆发痛快

《凡人修仙传》标准：
- 严谨：细节自洽，逻辑通顺
- 节奏：稳扎稳打，不急不躁
- 资源：交代清楚，不乱开挂
- 核心：猥琐发育，不浪

《诡秘之主》标准：
- 伏笔：埋下有回收
- 悬念：层层递进
- 世界观：自洽完整
- 核心：智斗解谜

《雪中悍刀行》标准：
- 文笔：优美流畅
- 人物：立体鲜活
- 情感：家国情怀
- 核心：江湖情义

《诛仙》标准：
- 情感：真挚动人
- 情节：感人肺腑
- 人物：成长蜕变
- 核心：爱恨情仇

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
   - 憋屈是否到位

【扣分项】

- 开局堆设定：-10分
- 主角装逼太刻意：-5分
- 反派智商下线：-5分
- 情节拖沓：-5分/1000字
- 逻辑不通：-10分
- AI味太重：-15分

【加分项】

- 开局炸弹：+5分
- 反转精彩：+5分
- 伏笔回收：+5分
- 情感动人：+5分

请严格按照以上标准进行审计。"""
    
    def audit_chapter(
        self,
        chapter_content: str,
        chapter_num: int,
        genre: str
    ) -> AuditResult:
        """审计章节质量"""
        if not self.llm:
            return self._fallback_audit(chapter_content, chapter_num)
        
        prompt = f"""请审计第{chapter_num}章的质量：

题材：{genre}

章节内容：
{chapter_content[:3000]}

请从以下维度评分：
1. 剧情逻辑（30分）
2. 节奏把控（25分）
3. 人物塑造（20分）
4. 文字质量（15分）
5. 爽点设计（10分）

总分：100分
及格线：60分

请给出：
- 总分
- 各维度得分
- 问题列表
- 改进建议
"""
        
        response = self.llm.generate(
            system_prompt=self.get_system_prompt(),
            user_prompt=prompt,
            max_tokens=1000,
            temperature=0.5
        )
        
        return self._parse_audit_response(response, chapter_content)
    
    def audit_continuity(
        self,
        current_chapter: str,
        previous_chapters: List[str]
    ) -> Dict[str, Any]:
        """审计连续性"""
        issues = []
        suggestions = []
        
        prev_text = " ".join(previous_chapters[-3:]) if previous_chapters else ""
        
        if not prev_text:
            return {
                "has_issues": False,
                "issues": [],
                "suggestions": ["暂无前文可对比"]
            }
        
        inconsistencies = self._check_basic_continuity(current_chapter, prev_text)
        issues.extend(inconsistencies)
        
        if len(issues) > 3:
            suggestions.append("建议检查人物设定一致性")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def audit_world_consistency(
        self,
        chapter_content: str,
        world_settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """审计世界观一致性"""
        issues = []
        suggestions = []
        
        power_levels = world_settings.get("power_levels", [])
        if power_levels:
            level_mentioned = self._check_power_level_mentions(chapter_content, power_levels)
            if level_mentioned:
                issues.append(f"提到了境界：{level_mentioned}")
        
        regions = world_settings.get("regions", [])
        if regions:
            region_mentioned = self._check_region_mentions(chapter_content, regions)
            if region_mentioned:
                issues.append(f"提到了地域：{region_mentioned}")
        
        return {
            "has_issues": len(issues) > 0,
            "issues": issues,
            "suggestions": suggestions
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
    
    def _fallback_audit(self, content: str, chapter_num: int) -> AuditResult:
        """备用审计"""
        word_count = len(content)
        
        score = 70.0
        issues = []
        suggestions = []
        
        if word_count < 1500:
            score -= 10
            issues.append("字数偏少，建议2000-3000字")
        elif word_count > 5000:
            score -= 5
            issues.append("字数偏多，建议控制在3000字左右")
        
        ai_check = self.audit_ai_tells(content)
        if ai_check["severity"] == "high":
            score -= 15
            issues.append("AI特征明显，需要改写")
        elif ai_check["severity"] == "medium":
            score -= 5
        
        if score >= 60:
            passed = True
        else:
            passed = False
            suggestions.append("需要大幅修改")
        
        return AuditResult(
            score=score,
            issues=issues,
            suggestions=suggestions,
            passed=passed
        )
    
    def _parse_audit_response(
        self,
        response: str,
        content: str
    ) -> AuditResult:
        """解析审计响应"""
        try:
            score = 70.0
            issues = []
            suggestions = []
            
            lines = response.split('\n')
            for line in lines:
                if '总分' in line or 'score' in line.lower():
                    try:
                        score = float(''.join(filter(lambda x: x.isdigit() or x == '.', line)))
                    except:
                        pass
            
            ai_check = self.audit_ai_tells(content)
            if ai_check["severity"] == "high":
                score = min(score, 60)
                issues.append("AI特征明显")
            
            return AuditResult(
                score=score,
                issues=issues,
                suggestions=suggestions,
                passed=score >= 60
            )
        except:
            return self._fallback_audit(content, 1)
    
    def _check_basic_continuity(self, current: str, previous: str) -> List[str]:
        """基本连续性检查"""
        issues = []
        
        if len(previous) > 100 and len(current) > 100:
            if "上章" in current or "上一章" in current:
                if "前文" not in previous:
                    issues.append("引用前文但描述不一致")
        
        return issues
    
    def _check_power_level_mentions(
        self,
        text: str,
        power_levels: List[str]
    ) -> List[str]:
        """检查境界提及"""
        mentioned = []
        for level in power_levels:
            if level in text:
                mentioned.append(level)
        return mentioned
    
    def _check_region_mentions(
        self,
        text: str,
        regions: List[str]
    ) -> List[str]:
        """检查地域提及"""
        mentioned = []
        for region in regions:
            if region in text:
                mentioned.append(region)
        return mentioned
