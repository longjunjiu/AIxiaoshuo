"""
题材规则 - 各类型网文创作规范
参考十大经典网文：玄幻、仙侠、都市等各题材写法
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class GenreTemplate:
    """题材模板"""
    name: str
    tropes: List[str]
    must_have: List[str]
    avoid: List[str]
    pacing: str
    example_novels: List[str]


class GenreRules:
    """
    题材规则引擎
    
    参考十大经典网文各题材写法：
    - 玄幻：《斗破苍穹》《神墓》《遮天》
    - 仙侠：《凡人修仙传》《诛仙》
    - 都市：《全职高手》
    - 悬疑：《诡秘之主》
    - 武侠：《雪中悍刀行》
    """
    
    GENRE_TEMPLATES = {
        "xuanhuan": GenreTemplate(
            name="玄幻",
            tropes=[
                "废柴逆袭", "退婚流", "三年之约",
                "丹药系统", "血脉觉醒", "师徒传承",
                "宗门争锋", "天才陨落", "王者归来"
            ],
            must_have=[
                "修炼境界体系",
                "功法等级设定",
                "势力分布",
                "地图升级（低级→中级→高级世界）"
            ],
            avoid=[
                "主角无敌碾压",
                "反派智商下线",
                "感情线狗血三角恋",
                "升级太快缺乏积累"
            ],
            pacing="打怪升级→境界突破→新地图→更强的敌人",
            example_novels=["斗破苍穹", "神墓", "遮天", "完美世界"]
        ),
        
        "xianxia": GenreTemplate(
            name="仙侠",
            tropes=[
                "修仙问道", "飞升传说", "三界六道",
                "神兵利器", "丹药灵草", "洞天福地",
                "心魔考验", "渡劫飞升", "长生不老"
            ],
            must_have=[
                "修仙境界体系（炼气→渡劫）",
                "天地灵气设定",
                "人神魔妖设定",
                "因果报应"
            ],
            avoid=[
                "修仙者像凡人一样争斗",
                "忽视心性修为",
                "境界突破太随意"
            ],
            pacing="积累修为→心性成长→渡劫→飞升",
            example_novels=["凡人修仙传", "诛仙", "仙逆", "求魔"]
        ),
        
        "urban": GenreTemplate(
            name="都市",
            tropes=[
                "扮猪吃虎", "富二代", "兵王回归",
                "医生/特种兵", "总裁文", "风水相术",
                "直播/电竞", "系统流", "神医"
            ],
            must_have=[
                "都市背景接地气",
                "主角隐藏身份",
                "打脸情节爽快",
                "人脉关系网"
            ],
            avoid=[
                "背景太脱离现实",
                "配角脸谱化",
                "情节重复打脸"
            ],
            pacing="低调装逼→被打脸→展现实力→收服",
            example_novels=["全职高手", "余罪", "大王饶命"]
        ),
        
        "xiuzhen": GenreTemplate(
            name="修真",
            tropes=[
                "凡人流", "稳健流", "苟道流",
                "资源积累", "阵法符箓", "炼丹炼器",
                "势力经营", "门派发展"
            ],
            must_have=[
                "详细的修炼资源体系",
                "炼丹/炼器/阵法技能树",
                "势力发展线",
                "资源争夺"
            ],
            avoid=[
                "主角到处浪",
                "遇到强者不跑",
                "越级挑战太轻松"
            ],
            pacing="猥琐发育→资源积累→势力壮大→一鸣惊人",
            example_novels=["凡人修仙传", "仙界走私大亨"]
        ),
        
        "kehuan": GenreTemplate(
            name="科幻",
            tropes=[
                "星际探索", "机甲战舰", "基因进化",
                "末世生存", "虚拟现实", "时间旅行",
                "人工智能", "外星文明"
            ],
            must_have=[
                "科技体系自洽",
                "宏大世界观",
                "文明冲突",
                "人类命运"
            ],
            avoid=[
                "科技设定前后矛盾",
                "忽视物理规律",
                "主角光环过重"
            ],
            pacing="探索→发现→危机→突破→新发现",
            example_novels=["三体", "吞噬星空", "地球纪元"]
        ),
        
        "xuanyi": GenreTemplate(
            name="悬疑/推理",
            tropes=[
                "密室杀人", "不可能犯罪", "心理博弈",
                "高智商犯罪", "连续杀人", "记忆碎片",
                "双重人格", "惊天反转"
            ],
            must_have=[
                "严密的逻辑推理",
                "线索公平布置",
                "悬念层层递进",
                "意想不到但合情合理的结局"
            ],
            avoid=[
                "线索不公平布置",
                "凶手随机选择",
                "靠巧合破案"
            ],
            pacing="案件发生→线索收集→推理分析→锁定凶手→真相大白",
            example_novels=["死亡通知单", "心理罪"]
        ),
        
        "wuxia": GenreTemplate(
            name="武侠",
            tropes=[
                "江湖恩怨", "武功秘籍", "门派之争",
                "侠客义气", "快意恩仇", "绝世神功",
                "江湖规矩", "正邪对立"
            ],
            must_have=[
                "武功体系完整",
                "江湖规矩",
                "人物侠义精神",
                "兵器暗器"
            ],
            avoid=[
                "武功像玄幻一样毁天灭地",
                "人物没有侠义精神",
                "脱离江湖规矩"
            ],
            pacing="初入江湖→得罪强敌→偶得秘籍→苦练武功→江湖扬名",
            example_novels=["雪中悍刀行", "死人经", "英雄志"]
        ),
        
        "tongren": GenreTemplate(
            name="同人",
            tropes=[
                "原著角色互动", "剧情穿越", "系统辅助",
                "角色觉醒", "位面旅行"
            ],
            must_have=[
                "熟悉原著剧情",
                "符合原著人设",
                "合理利用已知剧情"
            ],
            avoid=[
                "OOC（Out Of Character）",
                "强行改变原著设定",
                "破坏原著平衡"
            ],
            pacing="进入世界→了解剧情→介入改变→收获成长",
            example_novels=["穿越万界", "诸天万界"]
        )
    }
    
    # 各题材爽点设计
    GENRE_SHUANGDIAN = {
        "xuanhuan": [
            "打脸嘲讽者",
            "境界突破",
            "获得宝物/传承",
            "打败天才",
            "宗门大比夺冠",
            "越级战斗胜利"
        ],
        "xianxia": [
            "顿悟突破",
            "渡劫成功",
            "获得上古传承",
            "心魔被克服",
            "飞升仙界"
        ],
        "urban": [
            "打脸装逼者",
            "被误解→被崇拜",
            "英雄救美",
            "商业谈判胜利",
            "隐藏身份曝光"
        ],
        "xiuzhen": [
            "炼制成功高级丹药",
            "阵法困住敌人",
            "资源争夺胜利",
            "势力扩张",
            "发现秘境"
        ],
        "wuxia": [
            "比武胜利",
            "获得秘籍",
            "行侠仗义",
            "江湖地位提升",
            "报得大仇"
        ]
    }
    
    # 各题材节奏模板
    GENRE_PACING = {
        "xuanhuan": {
            "chapter_pacing": "每章必须有战斗/冲突/收获",
            "arc_length": "3-5章完成一个小高潮",
            "upgrade_interval": "每20-30章一次大升级",
            "cliffhanger": "每章结尾留悬念或爽点"
        },
        "xianxia": {
            "chapter_pacing": "修炼+人际+危机交替",
            "arc_length": "10-20章一个境界",
            "upgrade_interval": "大境界跨越需要情节推动",
            "cliffhanger": "心魔/天劫等危机时刻"
        },
        "urban": {
            "chapter_pacing": "装逼打脸循环",
            "arc_length": "2-3章一个小事件",
            "upgrade_interval": "人脉/地位稳步提升",
            "cliffhanger": "身份暴露危机"
        },
        "xiuzhen": {
            "chapter_pacing": "资源获取+修炼+布局",
            "arc_length": "5-10章一个小布局",
            "upgrade_interval": "稳扎稳打，不激进",
            "cliffhanger": "阴谋被揭露"
        }
    }
    
    def __init__(self, genre: str = "xuanhuan"):
        self.current_genre = genre
        self.template = self.GENRE_TEMPLATES.get(genre)
    
    def set_genre(self, genre: str):
        self.current_genre = genre
        self.template = self.GENRE_TEMPLATES.get(genre, self.GENRE_TEMPLATES["xuanhuan"])
    
    def get_tropes(self) -> str:
        if not self.template:
            return ""
        return f"""
【{self.template.name}题材经典套路】
{chr(10).join(['- ' + t for t in self.template.tropes])}
"""
    
    def get_must_have(self) -> str:
        if not self.template:
            return ""
        return f"""
【{self.template.name}题材必备元素】
{chr(10).join(['- ' + m for m in self.template.must_have])}
"""
    
    def get_avoid(self) -> str:
        if not self.template:
            return ""
        return f"""
【{self.template.name}题材避免事项】
{chr(10).join(['- ' + a for a in self.template.avoid])}
"""
    
    def get_shuangdian(self) -> str:
        shuangdian = self.GENRE_SHUANGDIAN.get(self.current_genre, [])
        return f"""
【{self.template.name if self.template else "通用"}爽点设计】
{chr(10).join(['- ' + s for s in shuangdian])}
"""
    
    def get_pacing_guide(self) -> str:
        pacing = self.GENRE_PACING.get(self.current_genre, {})
        return f"""
【节奏指导】
- 章节节奏: {pacing.get('chapter_pacing', '根据剧情需要')}
- 剧情弧长度: {pacing.get('arc_length', '根据剧情需要')}
- 升级间隔: {pacing.get('upgrade_interval', '根据剧情需要')}
- 悬念设置: {pacing.get('cliffhanger', '根据剧情需要')}
"""
    
    def get_classic_novels(self) -> str:
        if not self.template:
            return ""
        return f"""
【参考经典作品】
{chr(10).join(['- 《' + n + '》' for n in self.template.example_novels])}
"""
    
    def get_full_genre_prompt(self) -> str:
        return f"""
# {self.current_genre} 题材创作规范

{self.get_tropes()}
{self.get_must_have()}
{self.get_avoid()}
{self.get_shuangdian()}
{self.get_pacing_guide()}
{self.get_classic_novels()}

请严格按照以上{self.current_genre}题材规范进行创作。
"""
    
    def get_all_genres_prompt(self) -> str:
        return """
# 题材通用创作规范

## 十大经典网文题材参考

### 玄幻（《斗破苍穹》《遮天》《完美世界》）
- 核心：废柴逆袭、升级打怪
- 节奏：打怪→升级→打脸→更强的敌人
- 必备：境界体系、宗门势力、资源争夺

### 仙侠（《凡人修仙传》《诛仙》）
- 核心：修仙问道、飞升长生
- 节奏：积累修为→心性成长→渡劫飞升
- 必备：灵气设定、因果报应、心魔考验

### 都市（《全职高手》《余罪》）
- 核心：扮猪吃虎、打脸爽文
- 节奏：低调→被打脸→展现实力→收服
- 必备：都市背景接地气、隐藏身份

### 修真/凡人流（《凡人修仙传》）
- 核心：稳健苟道、资源积累
- 节奏：猥琐发育→资源积累→势力壮大
- 必备：炼丹炼器、势力发展线

### 武侠（《雪中悍刀行》）
- 核心：江湖恩怨、侠客义气
- 节奏：初入江湖→获得秘籍→江湖扬名
- 必备：武功体系、江湖规矩

### 科幻（《三体》《吞噬星空》）
- 核心：星际探索、科技设定
- 节奏：探索→发现→危机→突破
- 必备：科技自洽、宏大世界观

### 悬疑（《心理罪》）
- 核心：逻辑推理、层层悬念
- 节奏：案件→线索→推理→真相
- 必备：线索公平、反转合理

请根据所选题材，严格遵守以上创作规范。
"""
