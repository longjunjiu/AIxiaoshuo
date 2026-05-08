"""
创作规则 - 通用创作原则和技法
参考《斗破苍穹》《凡人修仙传》《诡秘之主》等十大经典网文
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CharacterTemplate:
    """角色模板"""
    name: str
    role: str
    sliders: Dict[str, float]
    wound: str
    want: str
    need: str
    lie: str
    ghost: str
    
    def to_prompt_context(self) -> str:
        return f"""
{self.name} ({self.role})
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
    """节拍模板"""
    name: str
    position: float
    description: str
    checklist: List[str]


class CraftRules:
    """
    创作规则引擎
    
    整合小说创作的核心技法和规则，参考十大经典网文：
    - 《斗破苍穹》- 废柴逆袭巅峰
    - 《凡人修仙传》- 凡人流开创者
    - 《诡秘之主》- 创新派神作
    - 《雪中悍刀行》- 文青融合典范
    - 《诛仙》- 仙侠经典
    """
    
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
        BeatTemplate("最终镜像", 0.99, "展示转变", ["与开场镜像"])
    ]
    
    SLIDER_RANGES = {
        "proactivity": (0, 10),
        "likability": (0, 10),
        "competence": (0, 10)
    }
    
    SCENE_OUTCOMES = {
        "yes_but": "目标达成但有新问题",
        "no_and": "目标失败且情况恶化",
        "yes_and": "目标达成且情况改善",
        "no_but": "目标失败但有转机"
    }
    
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
        self.genre = genre
    
    def get_beats_for_position(self, novel_length: int, current_position: int) -> List[BeatTemplate]:
        ratio = current_position / novel_length
        nearby_beats = []
        
        for beat in self.BEAT_SHEET:
            if abs(beat.position - ratio) < 0.15:
                nearby_beats.append(beat)
        
        return nearby_beats
    
    def get_arc_guidance(self, character: CharacterTemplate) -> str:
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
        return """
展示优于讲述规则：

禁止模式：
- "[角色]感到[情绪]" / "是[情绪]" / "似乎[情绪]"
- 情绪词作为叙述：愤怒、悲伤、快乐、恐惧
- 情绪副词：愤怒地、悲伤地、快乐地
- 特质声明："[角色]是[特质]"
- 关系声明："他们是最好的朋友"

例外情况：
- 时间过渡："三周后"
- 日常语境："她是个护士"（不关键时）
- 第一人称叙述者自然讲述自己的感受

关键时刻（情感高潮、揭露、高潮）应该：
- 零讲述，全展示
- 用动作、感官细节、对话传达
"""
    
    def get_dialogue_rules(self) -> str:
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
"""
    
    def get_magic_system_rules(self) -> str:
        return """
Sanderson魔法三定律：

零律："总是偏向于awesome一边。"

一定律："用魔法解决问题的能力与读者对魔法的理解程度成正比。"

二定律："限制 > 能力"
- 限制：硬边界（不能做什么）
- 代价：使用者付出的代价（消耗、生命力、资源）
- 弱点：它创造的弱点

三定律："先扩展已有的，再添加新的。"
"""
    
    def get_foreshadow_rules(self) -> str:
        return """
伏笔双向规则：

规则1（铺垫 -> 回收）：
每个显著引入的元素必须后来有叙事用途。

规则2（回收 -> 铺垫）：
高潮中使用的每个重要元素必须之前被引入。

伏笔类型：
1. 直接：预言、警告、关于未来的陈述
2. 象征：代表未来事件的对象/图像
3. 对话：后来才理解的双关
4. 行动：预览更大事件的小事件

规则：
- 铺垫和回收之间至少一个场景分离
- 三的法则：重要线索约3次引用后再回收
"""
    
    def get_stability_trap_warning(self) -> str:
        return """
稳定性陷阱警告：

研究发现：AI故事偏向稳定而非改变。这对小说来说是致命的。

具体失败模式：
- 角色抗拒转变
- 冲突解决太快太干净
- AI避免真正的黑暗、道德模糊、不可逆损失
- 没有信息经济：AI立即揭示一切
- 情感室温：一切保持在同一水平

对抗措施（主动执行）：
- 角色必须真正不同于开始时的样子
- 让坏事保持坏事
- 允许不可逆的决定和不可逆的损失
- 扣留信息。读者不应该知道一切。
- 变化情感强度：安静场景、爆发场景、恐惧、释然、无聊、惊奇、恐怖
"""
    
    def get_prose_guidance(self) -> str:
        return """
最佳奇幻散文的特点：

风格不是装饰——它就是奇幻本身。
语言不描述世界；语言创造世界。

最佳奇幻散文做到的：
1. 具体性：不是"一只鸟"而是"一只松鸦"
2. 惊喜：读者无法预测的用词选择
3. 节奏变化：短。然后长句子。然后再短。
4. 潜台词：没说的和说了的一样重要
5. 挣来的隐喻：来自角色经验的隐喻
6. 感官接地：锚定在特定感官上
7. 克制：从不放入的东西中获得力量
8. 安静时刻：不是每个场景都是动作
"""
    
    def get_novel_classic_prompts(self) -> str:
        return """
【十大经典网文写作风格参考】

《斗破苍穹》（废柴逆袭巅峰）
- 三年之约：目标明确，读者有期待
- 退婚流：开局冲突强
- 升级打怪：节奏明快，爽点密集
- 核心：憋屈→爆发→升级→更强的敌人
- 关键技巧：打脸要干脆利落，憋屈要憋到位

《凡人修仙传》（凡人流开创者）
- 低调谨慎：韩立性格，不浪
- 资源积累：每一步都算计
- 升级慢热：稳扎稳打
- 核心：闷声发大财
- 关键技巧：不要浪，每一步都要有收获

《诡秘之主》（创新派神作）
- 世界观独特：克苏鲁+蒸汽朋克
- 人物塑造：每个角色都有深度
- 悬念设置：层层迷雾，引人入胜
- 核心：智斗解谜
- 关键技巧：世界观要自洽，伏笔要回收

《雪中悍刀行》（文青融合）
- 文笔优美：武侠与玄幻结合
- 人物群像：每个角色都有故事
- 情感细腻：家国情怀、兄弟情义
- 核心：江湖不只是打打杀杀
- 关键技巧：人物要有血有肉，不脸谱化

《诛仙》（仙侠经典）
- 情感主线：张小凡的三段感情
- 世界观：天地不仁，以万物为刍狗
- 人物成长：从平凡到伟大
- 核心：修仙路上的爱恨情仇
- 关键技巧：情感要真实，不狗血

《全职高手》（职业电竞）
- 专业细节：游戏机制真实
- 团队配合：不是一个人的战斗
- 人物魅力：每个角色都有粉丝
- 核心：热爱与坚持
- 关键技巧：专业但不枯燥
"""
    
    def get_all_rules_prompt(self) -> str:
        return f"""
# 小说创作规则

## 十大经典网文参考
{self.get_novel_classic_prompts()}

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
        lines = ["\n节拍表（Save the Cat结构）：\n"]
        for beat in self.BEAT_SHEET:
            lines.append(f"- {beat.name} ({beat.position*100:.0f}%): {beat.description}")
        return "\n".join(lines)
