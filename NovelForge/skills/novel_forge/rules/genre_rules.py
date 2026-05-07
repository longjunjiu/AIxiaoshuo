"""
题材规则 - 各题材专属创作规则
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class GenreRules:
    """题材规则"""
    name: str
    name_en: str
    prohibitions: List[str]
    fatigue_words: List[str]
    language_rules: List[Dict[str, str]]
    audit_dimensions: List[int]
    rhythm_patterns: Dict[str, Any]
    
    def to_prompt(self) -> str:
        lines = [
            f"# {self.name}题材创作规则",
            "",
            "## 禁止事项",
        ]
        for pro in self.prohibitions:
            lines.append(f"- {pro}")
        
        lines.extend([
            "",
            "## 疲劳词",
            f"以下词汇应避免重复使用: {', '.join(self.fatigue_words)}"
        ])
        
        if self.language_rules:
            lines.extend(["", "## 语言规则"])
            for rule in self.language_rules:
                lines.append(f"- ✗ {rule.get('wrong', '')} → ✓ {rule.get('correct', '')}")
        
        return "\n".join(lines)


class GenreRuleManager:
    """题材规则管理器"""
    
    GENRES = {
        "xuanhuan": GenreRules(
            name="玄幻",
            name_en="Fantasy/Xuanhuan",
            prohibitions=[
                "主角关键时刻心软",
                "无意义的后宫暧昧拖剧情",
                "配角戏份喧宾夺主",
                "越级挑战无代价",
                "资源获取太容易",
                "境界突破无铺垫"
            ],
            fatigue_words=[
                "瞳孔骤缩", "不可置信", "倒吸一口凉气", "浑身一颤",
                "面色一沉", "勃然大怒", "心中一凛", "暗暗想到",
                "只见", "但见", "骤然", "霎时"
            ],
            language_rules=[
                {"wrong": "火元从12缕增加到24缕", "correct": "手臂比先前有力了，握拳时指骨发紧"},
                {"wrong": "他的修为提升了一大截", "correct": "枯坐三日后，他睁开眼，面前那盏长明灯熄了"},
                {"wrong": "这个天才真是太厉害了", "correct": "测试碑上，金光冲天而起"},
                {"wrong": "他感到非常震惊", "correct": "他后退了一步，撞翻了身后的椅子"}
            ],
            audit_dimensions=list(range(1, 27)),
            rhythm_patterns={
                "upgrade_rhythm": "瓶颈-顿悟-突破-巩固",
                "conflict_pattern": "挑衅-受辱-爆发-碾压",
                "climax_types": ["越级挑战", "宝物争夺", "势力对决"]
            }
        ),
        
        "xianxia": GenreRules(
            name="仙侠",
            name_en="Xianxia",
            prohibitions=[
                "修仙者轻易动凡心",
                "法宝获取无代价",
                "心魔无实际威胁",
                "渡劫如同喝水",
                "天道规则随意打破"
            ],
            fatigue_words=[
                "灵光一闪", "福至心灵", "道心微动", "元婴出窍",
                "天劫降临", "紫雷滚滚", "祥云缭绕"
            ],
            language_rules=[
                {"wrong": "他的法力深厚无比", "correct": "一袖挥出，千里之内风雨骤停"},
                {"wrong": "这是绝世功法", "correct": "功法残卷上，每一字都在流血"},
                {"wrong": "他顿悟了", "correct": "枯坐七七四十九天后，他对着月亮笑了一声"}
            ],
            audit_dimensions=list(range(1, 27)),
            rhythm_patterns={
                "cultivation_rhythm": "吸收-炼化-沉淀-突破",
                "dao_seeking": "问道-悟道-证道-传道"
            }
        ),
        
        "urban": GenreRules(
            name="都市",
            name_en="Urban/Modern",
            prohibitions=[
                "主角开篇无敌",
                "所有富二代都是反派",
                "商业竞争无脑化",
                "感情线狗血三角恋",
                "能力来源不解释"
            ],
            fatigue_words=[
                "邪魅一笑", "三分凉薄", "七分讥讽", "剑眉星目",
                "身材高挑", "气质出众", "不可名状"
            ],
            language_rules=[
                {"wrong": "迅速分析了当前的债务状况", "correct": "把那叠皱巴巴的白条翻了三遍"},
                {"wrong": "心中涌起一股暖流", "correct": "他没说话，只是把外套披在了她肩上"},
                {"wrong": "霸道总裁范", "correct": "他看了看表，'我还有五分钟'"}
            ],
            audit_dimensions=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            rhythm_patterns={
                "conflict_pattern": "冲突-对峙-转机-解决",
                "timeline_check": "年代考据必须准确"
            }
        ),
        
        "scifi": GenreRules(
            name="科幻",
            name_en="Science Fiction",
            prohibitions=[
                "违反已知物理定律",
                "科技解释模糊",
                "外星文明单一化",
                "忽略光年距离"
            ],
            fatigue_words=[
                "量子波动", "维度折叠", "暗能量", "平行宇宙"
            ],
            language_rules=[
                {"wrong": "他用意念控制了飞船", "correct": "脑波接口的指示灯亮了，飞船引擎嗡鸣着启动"},
                {"wrong": "这是一个高级文明", "correct": "戴森球包裹着恒星，舰队排列成完美的几何阵列"}
            ],
            audit_dimensions=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16],
            rhythm_patterns={
                "tech_reveal": "现象-猜测-验证-应用",
                "mystery_pattern": "谜题-线索-推理-真相"
            }
        ),
        
        "horror": GenreRules(
            name="恐怖",
            name_en="Horror",
            prohibitions=[
                "jump scare过度使用",
                "鬼魂能力无限制",
                "主角作死无逻辑",
                "血腥描写为血腥而血腥"
            ],
            fatigue_words=[
                "毛骨悚然", "不寒而栗", "一阵凉意", "浑身发抖",
                "黑暗中似乎有什么", "隐约听到"
            ],
            language_rules=[
                {"wrong": "感到一阵恐惧", "correct": "后颈的汗毛一根根立起来"},
                {"wrong": "房间里很安静", "correct": "三分钟后，他数清了墙上的裂纹——和他进门时看到的不一样"},
                {"wrong": "他慢慢走向黑暗", "correct": "手电筒的光圈越来越小"}
            ],
            audit_dimensions=[1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16, 22, 25],
            rhythm_patterns={
                "tension_build": "平静-异象-加剧-爆发",
                "fear_layers": "生理恐惧-心理恐惧-存在恐惧"
            }
        ),
        
        "general": GenreRules(
            name="通用",
            name_en="General",
            prohibitions=[
                "流水账式叙述",
                "无意义的环境描写",
                "对话推动剧情而非行动"
            ],
            fatigue_words=[
                "突然", "然后", "接着", "最后", "终于"
            ],
            language_rules=[],
            audit_dimensions=list(range(1, 17)),
            rhythm_patterns={}
        )
    }
    
    @classmethod
    def get_genre(cls, genre_id: str) -> GenreRules:
        """获取题材规则"""
        return cls.GENRES.get(genre_id, cls.GENRES["general"])
    
    @classmethod
    def get_all_genres(cls) -> List[str]:
        """获取所有题材ID"""
        return list(cls.GENRES.keys())
    
    @classmethod
    def get_genre_prompt(cls, genre_id: str) -> str:
        """获取题材规则提示词"""
        genre = cls.get_genre(genre_id)
        return genre.to_prompt()
    
    @classmethod
    def get_audit_dimensions(cls, genre_id: str) -> List[int]:
        """获取题材应审计的维度"""
        genre = cls.get_genre(genre_id)
        return genre.audit_dimensions
