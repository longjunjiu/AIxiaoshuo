"""
修订者机器人 - 优化和改写
参考十大经典网文风格
"""

from typing import Dict, Any, List, Optional


class ReviserAgent:
    """修订者机器人"""
    
    def __init__(self, llm_client=None, project=None, anti_slop=None):
        self.llm = llm_client
        self.project = project
        self.anti_slop = anti_slop
    
    def get_system_prompt(self) -> str:
        return """你是一位顶尖网络小说修订师，精通网文风格。

【修订技巧】

1. 替换AI词汇
   - "眼中闪过一丝" → 改用动作描写
   - "缓缓地" → 删除或换词
   - "骤然" → 改用具体描写

2. 增强动作
   - 原：她很害怕
   - 改：她往后退了两步，声音发颤

3. 对话口语化
   - 原：我认为此言差矣
   - 改：这话说的不对

请严格按照以上技巧进行修订。"""
    
    def revise(
        self,
        original: str = "",
        audit_report: Dict = None,
        mode: str = "polish",
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """修订章节"""
        if not original:
            return {"revised": "", "changes": [], "success": False}
        
        revised = original
        
        revised = self.remove_ai_tells(revised)
        revised = self.fix_dialogue(revised)
        
        return {
            "revised": revised,
            "changes": ["去除AI特征", "修复对话"],
            "success": True
        }
    
    def remove_ai_tells(self, content: str) -> str:
        """去除AI特征"""
        replacements = {
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
            "不可置信": "愣住了"
        }
        
        result = content
        for old, new in replacements.items():
            if old in result:
                if new:
                    result = result.replace(old, new)
                else:
                    result = result.replace(old, "")
        
        result = self._fix_ai_patterns(result)
        
        return result
    
    def _fix_ai_patterns(self, text: str) -> str:
        """修复AI模式"""
        import re
        
        patterns = [
            (r'他的眼中闪过一丝[\w]+', '他攥紧拳头'),
            (r'她的眼中闪过一丝[\w]+', '她攥紧衣角'),
            (r'缓缓地([^\n]{5,})', r'\1'),
            (r'渐渐地([^\n]{5,})', r'\1'),
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def fix_dialogue(self, content: str) -> str:
        """修复对话"""
        formal_phrases = [
            ("我认为", "我觉得"),
            ("此言差矣", "你说的不对"),
            ("确实如此", "是啊"),
            ("诸位", "大家"),
            ("在下", ""),
            ("本座", ""),
            ("吾", "我")
        ]
        
        result = content
        for formal, casual in formal_phrases:
            result = result.replace(formal, casual)
        
        return result
