"""
创作规则 - 通用创作原则和技法
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CharacterTemplate:
    """角色模板"""
    name: str
    role: str  # protagonist, antagonist, supporting
    sliders: Dict[str, float]  # proactivity, likability, competence
    wound: str
    want: str
    need: str
    lie: str
    ghost: str
    
    def to_prompt_context(self) -> str:
        """转换为提示词上下文"""
        return f"""
{name} ({self.role})
- 主动性: {self.sliders.get('proactivity', 5)}/10
- 魅力: {self.sliders.get('likability', 5)}/10
- 能力: {self.sliders.get('competence', 5)}/10
- 创伤: {self.wound}
- 欲望: {self.want}
- 需要: {self.need}
- 谎言: {self.lie}
- 过往: {self.ghost}
"""


@dataclass  
class BeatTemplate:
    """节拍模板（Save the Cat结构）"""
    name: str
    position: float  # 0-1, 小说中的位置
    description: str
    checklist: List[str]


class CraftRules:
    """
    创作规则引擎
    
    整合小说创作的核心技法和规则，为AI写作提供指导框架
    """
    
    # Save the Cat节拍表
    BEAT_SHEET = [
        BeatTemplate("开场画面", 0.01, "展示主角在变革前的状态", ["建立日常世界", "展示核心性格"]),
        BeatTemplate("主题陈述", 0.05, "通过某角色暗示主题", ["用词隐晦，不说教"]),
        BeatTemplate("铺垫", 0.10, "建立角色和世界", ["植入种子", "建立关系"]),
        BeatTemplate("催化剂", 0.12, "打破平衡的事件", ["被动发生，非主角选择"]),
        BeatTemplate("辩论", 0.20, "主角挣扎是否行动", ["展示内心冲突"]),
        BeatTemplate("闯入新世界", 0.25, "主角选择进入未知", ["必须是主动选择"]),
        BeatTemplate("B故事", 0.30, "承载主题的次要关系", ["与A故事并行"]),
        BeatTemplate("趣味游戏", 0.40, "展示故事的核心吸引力", ["最有趣的场景"]),
        BeatTemplate("中点", 0.50, "假胜利或假失败，真实失败", ["节奏转折"]),
        BeatTemplate("坏人逼近", 0.60, "内外压力同时增加", ["盟友分裂"]),
        BeatTemplate("一无所有", 0.70, "最低点", ["某种形式的死亡"]),
        BeatTemplate("灵魂黑夜", 0.75, "内化主题教训", ["准备改变"]),
        BeatTemplate("闯入第三幕", 0.80, "新信息改变一切", ["通常来自B故事"]),
        BeatTemplate("最终对决", 0.90, "解决主要冲突", ["执行新计划"]),
        BeatTemplate(" "final_image", 0.99, "展示转变", ["与开场镜像"])
    ]
    
    # 角色三轴（Sanderson）
    SLIDER_RANGES = {
        "proactivity": (0, 10),  # 推动剧情 vs 被动反应
        "likability": (0, 10),   # 让读者共情 vs 冷漠疏离
        "competence": (0, 10)   # 能力强大 vs 能力不足
    }
    
    # 场景结果类型
    SCENE_OUTCOMES = {
        "yes_but": "目标达成但有新问题",
        "no_and": "目标失败且情况恶化",
        "yes_and": "目标达成且情况改善（高潮前少用）",
        "no_but": "目标失败但有转机"
    }
    
    # 小说类型关键字
    GENRE_TRAITS = {
        "fantasy": ["魔法", "异世界", "成长", "史诗"],
        "scifi": ["科技", "未来", "探索", "宇宙"],
        "romance": ["感情", "羁绊", "纠结", "甜蜜"],
        "mystery": ["线索", "推理", "悬念", "反转"],
        "thriller": ["紧张", "危机", "追逐", "悬念"],
        "horror": ["恐惧", "诡异", "压抑", "血腥"]
    }
    
    def __init__(self):
        self.genre = "general"
        self.tone = "neutral"
    
    def set_genre(self, genre: str):
        """设置当前题材"""
        self.genre = genre
    
    def get_beats_for_position(self, novel_length: int, current_position: int) -> List[BeatTemplate]:
        """获取当前位置对应的节拍"""
        ratio = current_position / novel_length
        nearby_beats = []
        
        for beat in self.BEAT_SHEET:
            if abs(beat.position - ratio) < 0.15:
                nearby_beats.append(beat)
        
        return nearby_beats
    
    def get_arc_guidance(self, character: CharacterTemplate) -> str:
        """获取角色弧线指导"""
        return f"""
角色弧线检查：
1. 开场：角色生活在谎言中，谎言"有效"
2. 催化剂：第一次触及真相
3. 第一情节点：谎言被直接挑战，但角色仍坚持
4. 上半场：基于谎言行动，收集工具
5. 中点：瞥见真相，从被动转为主动
6. 下半场：在谎言和真相之间摇摆
7. 第三情节点：谎言最坏后果暴露，必须选择
8. 高潮：选择真相，摒弃谎言（或反之）
9. 结局：在新的真相中生活，需求满足
"""
    
    def get_show_dont_tell_rules(self) -> str:
        """获取展示优于讲述规则"""
        return """
展示优于讲述规则：

禁止模式（regex可检测）：
- "[角色]感到[情绪]" / "是[情绪]" / "似乎[情绪]"
- 情绪词作为叙述：愤怒、悲伤、快乐、恐惧、紧张、兴奋
- 情绪副词：愤怒地、悲伤地、快乐地
- 特质声明："[角色]是[特质]"
- 关系声明："他们是最好的朋友"
- 氛围标签："这是一个诡异的房子"

例外情况：
- 时间过渡："三周后"
- 日常语境："她是个护士"（不关键时）
- 第一人称叙述者自然讲述自己的感受

关键时刻（情感高潮、揭露、高潮）应该：
- 零讲述，全展示
- 用动作、感官细节、对话传达
"""
    
    def get_dialogue_rules(self) -> str:
        """获取对话规则"""
        return """
对话可辨识性规则：

八个可测量维度：
1. 词汇水平（音节数、阅读级别）
2. 句子长度和结构（简洁 vs 冗长）
3. 缩写和正式程度
4. 口头禅和特有表达（每个角色独特）
5. 问句 vs 陈述句比例
6. 打断模式
7. 隐喻领域（士兵=军事隐喻，农民=土地隐喻）
8. 直接 vs 间接

测试：移除所有对话标签后，仍能分辨谁在说话吗？
- 如果能，对话有辨识度
- 如果不能，需要差异化
"""
    
    def get_magic_system_rules(self) -> str:
        """获取魔法系统规则"""
        return """
 Sanderson魔法三定律：

零律："总是偏向于awesome一边。" 奇迹有内在价值。

一定律："用魔法解决问题的能力与读者对魔法的理解程度成正比。"
- 硬魔法（规则清晰）可以解决问题
- 软魔法（神秘）应该制造问题
- 用未解释的魔法解决高潮冲突 = 机械降神

二定律："限制 > 能力"
- 限制：硬边界（不能做什么）
- 代价：使用者付出的代价（消耗、生命力、资源）
- 弱点：它创造的弱点（敌人可见等）
- 限制应在叙事中比能力更突出
- 代价应该推动情节决策

三定律："先扩展已有的，再添加新的。"
- 更少能力但更多应用 = 深度
- 更多能力但每个只有少量应用 = 杂货铺
- 最后25%不能出现未铺垫的新能力
"""
    
    def get_foreshadow_rules(self) -> str:
        """获取伏笔规则"""
        return """
伏笔双向规则：

规则1（铺垫 -> 回收）：
每个显著引入的元素必须后来有叙事用途。
如果它有自己的描述句、被多次提及、或在对话中被评论，它必须变得相关。

规则2（回收 -> 铺垫）：
高潮中使用的每个重要元素必须之前被引入。
高潮不能出现未铺垫的元素。

伏笔类型：
1. 直接：预言、警告、关于未来的陈述
2. 象征：代表未来事件的对象/图像
3. 对话：后来才理解的双关
4. 行动：预览更大事件的小事件
5. 标题/命名：有隐藏含义的章节标题或名字

规则：
- 铺垫和回收之间至少一个场景分离
- 三的法则：重要线索约3次引用后再回收
- 每个植入的线索必须解决（或作为红鲱鱼本身被解释）
"""
    
    def get_stability_trap_warning(self) -> str:
        """稳定性陷阱警告（AI最坏倾向）"""
        return """
稳定性陷阱警告：

研究发现：AI故事偏向稳定而非改变。这对小说来说是致命的。

具体失败模式：
- 角色抗拒转变
- 冲突解决太快太干净
- AI避免真正的黑暗、道德模糊、不可逆损失
- "你开始的尖锐点被磨圆成更模糊、更安全、更通用的东西"
- 没有信息经济：AI立即揭示一切，无法保持神秘或延迟回报
- 情感室温：一切保持在同一水平

对抗措施（主动执行）：
- 角色必须真正不同于开始时的样子
- 让坏事保持坏事。不是所有事都被修复。
- 允许不可逆的决定和不可逆的损失
- 扣留信息。读者不应该知道一切。
- 创造真正的道德模糊。让"正确"选择不清晰。
- 变化情感强度：安静场景、爆发场景、恐惧、释然、无聊、惊奇、恐怖。不是一条平线。
- 如果一个选择没有真正代价，它就不是真正的选择。
"""
    
    def get_prose_guidance(self) -> str:
        """获取散文指导（Le Guin风格）"""
        return """
最佳奇幻散文的特点（Le Guin核心洞察）：

风格不是装饰——它就是奇幻本身。
语言不描述世界；语言创造世界。
如果你的奇幻世界听起来像公交时刻表，你就没在写奇幻。

最佳奇幻散文做到的：
1. 具体性：不是"一只鸟"而是"一只松鸦"。不是"花"而是"羽扇豆"。
2. 惊喜：读者无法预测的用词选择。
3. 节奏变化：短。然后是带着读者前进的长句子。然后再短。
4. 潜台词：没说的和说了的一样重要。
5. 挣来的隐喻：来自角色经验的隐喻，不是同义词库。
6. 感官接地：锚定在特定感官上，不是抽象。
7. 克制：从不放入的东西中获得力量，不是一直堆砌。
8. 安静时刻：不是每个场景都是动作。角色坐着、思考、看着雨——这些让戏剧时刻落地。
"""
    
    def get_all_rules_prompt(self) -> str:
        """获取所有规则的提示词"""
        return f"""
# 小说创作规则

## 人物塑造
{self.get_arc_guidance(CharacterTemplate("", "", {}, "", "", "", "", ""))}

## 叙事技法
{self.get_show_dont_tell_rules()}

## 对话规则
{self.get_dialogue_rules()}

## 魔法/能力系统
{self.get_magic_system_rules()}

## 伏笔规则
{self.get_foreshadow_rules()}

## 稳定性陷阱警告
{self.get_stability_trap_warning()}

## 散文指导
{self.get_prose_guidance()}

## 节拍表（Save the Cat）
{self._format_beats()}

请严格遵守以上规则进行创作。
"""
    
    def _format_beats(self) -> str:
        """格式化节拍表"""
        lines = ["\n节拍表（Save the Cat结构）：\n"]
        for beat in self.BEAT_SHEET:
            lines.append(f"- {beat.name} ({beat.position*100:.0f}%): {beat.description}")
        return "\n".join(lines)
