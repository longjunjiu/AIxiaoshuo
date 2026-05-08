"""
修订者机器人 - 优化和改写
参考十大经典网文风格
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class RevisionTarget:
    """修订目标"""
    content: str
    issues: List[str]
    target_style: str


class ReviserAgent:
    """
    修订者机器人
    
    参考十大经典网文风格修订：
    - 《斗破苍穹》- 爽点密集、节奏明快
    - 《凡人修仙传》- 低调谨慎、稳扎稳打
    - 《诡秘之主》- 悬念迭起、智斗解谜
    - 《雪中悍刀行》- 文笔优美、人物立体
    - 《诛仙》- 情感真实、不狗血
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def get_system_prompt(self) -> str:
        return """你是一位顶尖网络小说修订师，精通网文风格。

【十大经典网文风格参考】

《斗破苍穹》风格：
- 爽点密集，打脸干脆
- 节奏明快，不拖沓
- 憋屈要憋到位，爆发要爆痛快
- 升级描写清晰

《凡人修仙传》风格：
- 低调谨慎
- 稳扎稳打
- 资源积累
- 不浪

《诡秘之主》风格：
- 悬念迭起
- 智斗解谜
- 伏笔回收
- 世界观自洽

《雪中悍刀行》风格：
- 文笔优美
- 人物立体
- 情感细腻
- 江湖情义

《诛仙》风格：
- 情感真挚
- 情节感人
- 人物成长
- 不狗血

【常见修订问题】

1. AI特征词汇
   - "眼中闪过一丝" → 改用动作描写
   - "缓缓地" → 删除或换词
   - "骤然" → 改用具体描写

2. 套路化表达
   - 减少情绪词直接陈述
   - 用动作和表情传达情感
   - 对话要口语化

3. 节奏问题
   - 开局拖沓 → 前300字扔炸弹
   - 中段拖沓 → 删除废话
   - 结尾仓促 → 增强悬念

4. 逻辑问题
   - 人物行为不一致 → 保持人设
   - 战力崩 → 保持等级设定
   - 剧情漏洞 → 填补漏洞

【修订技巧】

1. 替换AI词汇
   ```
   原：他的眼中闪过一丝坚定
   改：他攥紧拳头，指节发白
   ```

2. 增强动作
   ```
   原：她很害怕
   改：她往后退了两步，声音发颤
   ```

3. 对话口语化
   ```
   原：我认为此言差矣
   改：这话说的不对
   ```

4. 增加爽点
   ```
   原：主角赢了
   改：主角一巴掌扇过去，对方直接懵了
   ```

请严格按照以上技巧进行修订。"""
    
    def revise_chapter(
        self,
        content: str,
        issues: List[str],
        genre: str = "xuanhuan"
    ) -> str:
        """修订章节"""
        if not self.llm:
            return self._fallback_revise(content, issues)
        
        issue_str = "\n".join([f"- {issue}" for issue in issues])
        
        prompt = f"""请修订以下章节：

题材：{genre}

发现的问题：
{issue_str}

章节内容：
{content}

修订要求：
1. 解决所有问题
2. 保持网文风格
3. 增强爽点（如果是玄幻题材）
4. 减少AI特征
5. 对话口语化

请直接输出修订后的内容：
"""
        
        response = self.llm.generate(
            system_prompt=self.get_system_prompt(),
            user_prompt=prompt,
            max_tokens=len(content) * 2,
            temperature=0.7
        )
        
        return response
    
    def polish_chapter(
        self,
        content: str,
        target_style: str = "爽文"
    ) -> str:
        """润色章节"""
        if not self.llm:
            return content
        
        prompt = f"""请润色以下章节：

目标风格：{target_style}

章节内容：
{content}

润色要求：
1. 增强节奏感
2. 增加爽点
3. 减少拖沓
4. 保持人物性格

请直接输出润色后的内容：
"""
        
        response = self.llm.generate(
            system_prompt=self.get_system_prompt(),
            user_prompt=prompt,
            max_tokens=len(content) * 2,
            temperature=0.7
        )
        
        return response
    
    def remove_ai_tells(self, content: str) -> str:
        """去除AI特征"""
        replacements = {
            "眼中闪过一丝": "",
            "缓缓地": "",
            "渐渐地": "",
            "骤然": "突然",
            "霎时": "一瞬间",
            "登时": "立刻",
            "不由": "",
            "不禁": "",
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
        patterns = [
            (r'他的眼中闪过一丝[\w]+', '他攥紧拳头'),
            (r'她的眼中闪过一丝[\w]+', '她攥紧衣角'),
            (r'缓缓地([^\n]{5,})', r'\1'),
            (r'渐渐地([^\n]{5,})', r'\1'),
            (r'突然(，[^\n]{0,20}$)', r'\1'),
        ]
        
        for pattern, replacement in patterns:
            import re
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def enhance_shuangdian(self, content: str, genre: str = "xuanhuan") -> str:
        """增强爽点"""
        if genre not in ["xuanhuan", "urban"]:
            return content
        
        if not self.llm:
            return content
        
        prompt = f"""请增强以下章节的爽点：

题材：{genre}

章节内容：
{content}

爽点增强技巧：
1. 打脸场景：增加对方震惊、后悔的描写
2. 升级场景：增加异象、众人惊叹
3. 装逼场景：增加旁观者反应

请输出增强后的内容：
"""
        
        response = self.llm.generate(
            system_prompt=self.get_system_prompt(),
            user_prompt=prompt,
            max_tokens=len(content) * 2,
            temperature=0.8
        )
        
        return response
    
    def fix_dialogue(self, content: str) -> str:
        """修复对话"""
        formal_phrases = [
            ("我认为", "我觉得"),
            ("此言差矣", "你说的不对"),
            ("确实如此", "是啊"),
            ("不得不承认", "得说"),
            ("由此可见", "这么看"),
            ("综上所述", "说白了"),
            ("君不见", "你没看见吗"),
            ("诸位", "大家"),
            ("在下", ""),
            ("本座", ""),
            ("吾", "我")
        ]
        
        result = content
        for formal, casual in formal_phrases:
            result = result.replace(formal, casual)
        
        return result
    
    def add_cliffhanger(self, content: str, chapter_num: int) -> str:
        """添加章尾钩子"""
        if not self.llm:
            return content
        
        prompt = f"""请为以下章节添加结尾钩子：

章节：第{chapter_num}章

章节内容：
{content}

钩子要求：
1. 留下悬念
2. 引发好奇
3. 让读者想追下一章

请在结尾添加适当的钩子：
"""
        
        response = self.llm.generate(
            system_prompt=self.get_system_prompt(),
            user_prompt=prompt,
            max_tokens=500,
            temperature=0.8
        )
        
        lines = content.strip().split('\n')
        while lines and not lines[-1].strip():
            lines.pop()
        
        return '\n'.join(lines) + '\n\n' + response.strip()
    
    def _fallback_revise(
        self,
        content: str,
        issues: List[str]
    ) -> str:
        """备用修订"""
        result = content
        
        result = self.remove_ai_tells(result)
        result = self.fix_dialogue(result)
        
        return result
    
    def batch_revise(
        self,
        contents: List[str],
        issues_list: List[List[str]],
        genre: str = "xuanhuan"
    ) -> List[str]:
        """批量修订"""
        revised = []
        
        for content, issues in zip(contents, issues_list):
            revised_content = self.revise_chapter(content, issues, genre)
            revised.append(revised_content)
        
        return revised
