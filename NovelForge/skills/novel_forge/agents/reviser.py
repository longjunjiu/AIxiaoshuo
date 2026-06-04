"""
修订者机器人 - 优化和改写
参考十大经典网文风格
"""

import re
from typing import Dict, Any, List, Optional


class ReviserAgent:
    """修订者机器人"""

    AI_REPLACEMENTS = {
        "眼中闪过一丝": "",
        "缓缓地": "",
        "渐渐地": "",
        "骤然": "突然",
        "霎时": "一瞬间",
        "登时": "立刻",
        "心头一紧": "心里咯噔一下",
        "深吸一口气": "喘了口气",
        "嘴角微微上扬": "嘴角一勾",
        "脸上浮现": "脸上露出",
        "目光深邃": "眼神深沉",
        "浑身一颤": "打了个哆嗦",
        "倒吸一口凉气": "愣住了",
        "瞳孔骤缩": "愣住",
        "不可置信": "愣住了",
        "嘴角勾起": "嘴角一扯",
        "眼神复杂": "神情变了变"
    }

    FORMAL_TO_CASUAL = [
        ("我认为", "我觉得"),
        ("此言差矣", "你说的不对"),
        ("确实如此", "是啊"),
        ("诸位", "大家"),
        ("足下", "你"),
        ("尔等", "你们"),
    ]

    def __init__(self, llm_client=None, project=None, anti_slop=None):
        self.llm = llm_client
        self.project = project
        self.anti_slop = anti_slop

    def get_system_prompt(self) -> str:
        return """你是一位顶尖网络小说修订师，精通网文风格。

【核心修订原则】

1. 去AI感：消除机械化表达，让文字有呼吸感
   - "眼中闪过一丝xxx" → 改用具体动作
   - "深吸一口气" → 改用符合场景的细节
   - "缓缓地" → 直接删除或用具体动作替代

2. 增强感官：让读者"看见"而不是"被告知"
   - 原：他很愤怒
   - 改：他把茶杯往桌上一摔，瓷器碎了一地

3. 对话口语化：符合人物身份和场景
   - 保留方言特色、个性化用语
   - 删除过于书面的表达

4. 网文节奏感：短句制造紧张，长句营造氛围
   - 战斗场景：短句快节奏
   - 情感场景：适当放缓

直接输出修订后正文，不要输出其他说明。"""

    def revise(
        self,
        original: str = "",
        audit_report: Dict = None,
        mode: str = "polish",
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        修订章节

        Args:
            original: 原始内容
            audit_report: 审计报告
            mode: polish（润色）/ rewrite（重写）/ rework（深度改写）/ anti-detect（去AI检测）
            max_iterations: 最大迭代次数
        """
        if not original:
            return {"revised": "", "changes": [], "success": False}

        revised = original
        changes = []

        # Always apply static rule-based fixes first
        revised, static_changes = self._apply_static_fixes(revised)
        changes.extend(static_changes)

        # Use LLM for deeper revision when available
        if self.llm:
            try:
                if mode in ("polish", "anti-detect"):
                    llm_result = self._polish_with_llm(revised, audit_report)
                elif mode in ("rewrite", "rework"):
                    llm_result = self._rewrite_with_llm(revised, audit_report, mode)
                else:
                    llm_result = self._polish_with_llm(revised, audit_report)

                if llm_result.get("revised"):
                    revised = llm_result["revised"]
                    changes.extend(llm_result.get("changes", []))
            except Exception:
                pass

        return {
            "revised": revised,
            "original": original,
            "changes": changes,
            "success": True,
            "mode": mode,
            "word_count": len(revised)
        }

    def _apply_static_fixes(self, content: str) -> tuple:
        """应用静态规则修复，返回 (修复后内容, 变更列表)"""
        result = content
        changes = []

        # Replace AI tells
        ai_fixed = 0
        for old, new in self.AI_REPLACEMENTS.items():
            if old in result:
                result = result.replace(old, new) if new else result.replace(old, "")
                ai_fixed += 1

        if ai_fixed > 0:
            changes.append(f"替换{ai_fixed}处AI特征词汇")

        # Fix regex patterns
        patterns = [
            (r'他的眼中闪过一丝[\w]{1,4}', '他攥紧了拳头'),
            (r'她的眼中闪过一丝[\w]{1,4}', '她攥紧了衣角'),
            (r'缓缓地([^，。\n]{3,})', r'\1'),
            (r'渐渐地([^，。\n]{3,})', r'\1'),
            (r'不禁([^，。\n]{3,})', r'\1'),
        ]
        for pattern, replacement in patterns:
            new_result = re.sub(pattern, replacement, result)
            if new_result != result:
                result = new_result

        # Formal-to-casual dialogue fixes
        dialogue_fixed = 0
        for formal, casual in self.FORMAL_TO_CASUAL:
            if formal in result:
                result = result.replace(formal, casual)
                dialogue_fixed += 1

        if dialogue_fixed > 0:
            changes.append(f"口语化{dialogue_fixed}处书面用语")

        return result, changes

    def _polish_with_llm(self, content: str, audit_report: Dict = None) -> Dict[str, Any]:
        """使用LLM润色文本"""
        issues_text = ""
        if audit_report and audit_report.get('issues'):
            issues_text = "\n\n已知问题需改善：\n" + "\n".join(
                f"- {i}" for i in audit_report['issues'][:3]
            )

        prompt = f"""请对以下小说章节进行润色，目标：
1. 消除残余AI感，让文字更自然真实
2. 增强感官细节，用动作传达情绪
3. 保持网文节奏感，强化爽点
4. 保留原有情节和结构{issues_text}

原文：
{content[:5000]}

直接输出润色后的正文，不添加任何说明。"""

        response = self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.get_system_prompt(),
            temperature=0.6,
            max_tokens=min(len(content) + 800, 6000)
        )

        return {
            "revised": response.content.strip(),
            "changes": ["LLM润色优化"]
        }

    def _rewrite_with_llm(self, content: str, audit_report: Dict = None, mode: str = "rewrite") -> Dict[str, Any]:
        """使用LLM重写文本"""
        issues_text = ""
        if audit_report and audit_report.get('issues'):
            issues_text = "\n\n需要解决的问题：\n" + "\n".join(
                f"- {i}" for i in audit_report['issues'][:3]
            )

        depth = "深度改写，可以调整结构和表达" if mode == "rework" else "改写，保留情节框架"

        prompt = f"""请对以下小说章节进行{depth}：{issues_text}

参考原文（保留情节走向）：
{content[:3000]}

要求：
- 字数与原文相近（约{len(content)}字）
- 网文风格，爽点突出
- 无AI感，文字生动
- 对话口语化

直接输出改写后正文。"""

        response = self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            system=self.get_system_prompt(),
            temperature=0.75,
            max_tokens=min(len(content) + 1200, 6000)
        )

        return {
            "revised": response.content.strip(),
            "changes": [f"LLM{depth}"]
        }

    def remove_ai_tells(self, content: str) -> str:
        """去除AI特征词（向后兼容接口）"""
        result, _ = self._apply_static_fixes(content)
        return result

    def fix_dialogue(self, content: str) -> str:
        """修复对话（向后兼容接口）"""
        result = content
        for formal, casual in self.FORMAL_TO_CASUAL:
            result = result.replace(formal, casual)
        return result
