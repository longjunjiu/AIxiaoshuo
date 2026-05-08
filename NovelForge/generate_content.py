#!/usr/bin/env python3
"""
NovelForge 交互式内容生成器
每次询问都提供多个方案/思路供选择
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "skills"))


class NovelForgeInteractive:
    """交互式小说生成器"""

    # ============================================================================
    # 方案库 - 每个问题都有多个详细方案
    # ============================================================================

    NOVEL_TYPES = {
        "1": {
            "name": "玄幻",
            "description": "废柴逆袭、打怪升级、功法传承",
            "方案": [
                "退婚流：被未婚妻退婚，立下三年之约，经典开局",
                "灭门流：家族被灭，主角流落他乡，隐忍复仇",
                "血脉流：血脉觉醒，家族废物逆袭天才",
                "系统流：获得任务系统，兑换功法神器"
            ],
            "参考": ["《斗破苍穹》", "《完美世界》", "《万古最强宗》"]
        },
        "2": {
            "name": "仙侠",
            "description": "修仙问道、飞升长生、斩妖除魔",
            "方案": [
                "凡人流：资质平庸，一步一步稳扎稳打",
                "转世流：仙人转世，前世记忆觉醒",
                "问道流：追寻大道，探索长生奥秘",
                "斩妖流：下山历练，降妖除魔"
            ],
            "参考": ["《凡人修仙传》", "《仙逆》", "《求魔》"]
        },
        "3": {
            "name": "都市",
            "description": "扮猪吃虎、打脸爽文、暧昧都市",
            "方案": [
                "兵王流：特种兵王回归都市，低调装逼",
                "神医流：得传承，行医救人，桃运不断",
                "首富流：继承万亿家产，低调炫富",
                "直播流：直播日常，无意间火遍全网"
            ],
            "参考": ["《都市奇门医圣》", "《重生之都市修仙》", "《大王饶命》"]
        },
        "4": {
            "name": "修真",
            "description": "炼丹炼器、势力经营、苟道流",
            "方案": [
                "苟道流：低调发育，能不出手就不出手",
                "势力流：建立门派，发展势力，一统江湖",
                "丹道流：以炼丹为主，丹药换资源",
                "符阵流：以符箓阵法为主，越阶战斗"
            ],
            "参考": ["《凡人修仙传》", "《仙丹遍地》", "《修仙模拟器》"]
        },
        "5": {
            "name": "武侠",
            "description": "江湖恩怨、武功秘籍、侠客义气",
            "方案": [
                "少林流：少林寺出身，学七十二绝技",
                "古墓流：古墓派传人，绝世武功",
                "魔教流：魔教少主，正邪之争",
                "江湖流：江湖散人，快意恩仇"
            ],
            "参考": ["《雪中悍刀行》", "《死人经》", "《英雄志》"]
        },
        "6": {
            "name": "科幻",
            "description": "星际探索、机甲战舰、基因进化",
            "方案": [
                "星际流：星际殖民，探索宇宙奥秘",
                "机甲流：驾驶机甲，战力爆表",
                "基因流：基因改造，进化变强",
                "末世流：末日降临，生存挣扎"
            ],
            "参考": ["《吞噬星空》", "《三体》", "《地球纪元》"]
        },
        "7": {
            "name": "悬疑",
            "description": "逻辑推理、层层悬念、惊天反转",
            "方案": [
                "推理流：连环杀人案，层层剥茧",
                "盗墓流：古墓探险，机关重重",
                "灵异流：鬼怪作祟，驱魔捉鬼",
                "心理流：心理犯罪，高智商对决"
            ],
            "参考": ["《鬼吹灯》", "《盗墓笔记》", "《心理罪》"]
        },
        "8": {
            "name": "同人",
            "description": "原著角色、剧情穿越、位面旅行",
            "方案": [
                "综漫流：穿越多个动漫世界",
                "诸天流：进入电影、电视剧世界",
                "斗破流：进入斗破苍穹世界",
                "全职流：进入全职高手世界"
            ],
            "参考": ["《诸天万界》", "《穿越万界》", "《轮回乐园》"]
        }
    }

    CONFLICT_OPTIONS = {
        "1": {
            "name": "退婚流",
            "description": "经典开局，憋屈逆袭",
            "方案": [
                "被未婚妻退婚，受尽屈辱，立下三年之约",
                "被家族除名，逐出家门，三年后当众打脸",
                "被天才嘲笑婚约是耻辱，约定比武一决高下"
            ],
            "核心": "憋屈→隐忍→三年之约→打脸爆发"
        },
        "2": {
            "name": "灭门流",
            "description": "血海深仇，复仇主线",
            "方案": [
                "家族被灭，只有主角侥幸逃脱，誓要复仇",
                "父母被害，主角被追杀，流落他乡隐姓埋名",
                "宗门被灭，主角独活，暗中调查真相"
            ],
            "核心": "灭门→逃亡→隐忍→调查→复仇"
        },
        "3": {
            "name": "废物流",
            "description": "资质平庸，逆袭崛起",
            "方案": [
                "天生废脉，无法修炼，被人嘲笑",
                "资质低下，丹田破碎，被人看不起",
                "天生绝脉，被判定为废物，实则有隐藏体质"
            ],
            "核心": "被嘲→金手指→逆袭→打脸"
        },
        "4": {
            "name": "穿越流",
            "description": "穿越异世，重新开始",
            "方案": [
                "现代人穿越到玄幻世界，带有现代知识",
                "重生回到过去，带着前世记忆",
                "灵魂穿越到废柴身上，继承记忆和仇恨"
            ],
            "核心": "穿越→适应→利用优势→崛起"
        },
        "5": {
            "name": "争锋流",
            "description": "天才竞争，宗门争斗",
            "方案": [
                "进入顶级宗门，与天才弟子争斗",
                "宗门大比，争夺核心弟子之位",
                "天才选拔赛，脱颖而出"
            ],
            "核心": "入门→竞争→崛起→登顶"
        },
        "6": {
            "name": "逆袭流",
            "description": "屌丝逆袭，扮猪吃虎",
            "方案": [
                "身份卑微，实际是隐藏大佬",
                "表面废物，实际拥有逆天天赋",
                "隐藏身份，只有少数人知道真相"
            ],
            "核心": "隐藏→被打脸→暴露→震惊全场"
        }
    }

    GOLDEN_FINGERS = {
        "1": {
            "name": "系统",
            "description": "任务奖励、兑换商城、属性面板",
            "方案": [
                "神级选择系统：完成任务获得奖励，选对有额外加成",
                "超级商城系统：积分兑换功法、神器、丹药",
                "属性面板：可以看到自己和他人的属性",
                "签到系统：每日签到获得奖励，连续签到有惊喜"
            ],
            "参考": "系统流核心是任务驱动，主角被动变强"
        },
        "2": {
            "name": "老爷爷",
            "description": "神秘传承、辅助指导、功法灌输",
            "方案": [
                "戒指老爷爷：藏在戒指中的强者残魂",
                "器灵传承：神兵中的器灵传授功法",
                "师傅残魂：临死前将毕生所学传给主角",
                "灵魂契约：与强者灵魂签订契约，获得指导"
            ],
            "参考": "老爷爷流核心是有一个亦师亦友的存在"
        },
        "3": {
            "name": "神器",
            "description": "上古宝物、特殊能力、成长潜力",
            "方案": [
                "神秘小瓶：可以催熟灵药，加速修炼",
                "上古剑胚：蕴养剑意，不断进化",
                "空间神器：内有空间，储物+修炼",
                "九龙鼎：炼丹神器，丹药品质提升"
            ],
            "参考": "神器流核心是宝物本身有成长潜力"
        },
        "4": {
            "name": "体质",
            "description": "特殊体质、天生强大、隐藏觉醒",
            "方案": [
                "天生剑体：对剑道有天生亲和力",
                "重瞳体质：可以看到事物本质",
                "吞噬体质：可以吞噬他人修为",
                "轮回体质：死而复生，记忆叠加"
            ],
            "参考": "体质流核心是体质不断觉醒进化"
        },
        "5": {
            "name": "空间",
            "description": "独立空间、时间流速、资源产出",
            "方案": [
                "随身空间：可储物、可种植、可休息",
                "时间流速空间：空间内时间流速不同",
                "秘境空间：连接神秘秘境，获得机缘",
                "创造空间：可以创造物品、材料"
            ],
            "参考": "空间流核心是资源积累和战略优势"
        }
    }

    STYLE_REFERENCES = {
        "1": {
            "name": "《斗破苍穹》",
            "style": "爽点密集，打脸干脆",
            "核心技巧": [
                "憋屈要憋到位，让人看着憋屈想打人",
                "打脸要干脆利落，一巴掌扇过去",
                "升级要有仪式感，天地异象、众人震惊",
                "每章要有小爽点，每卷要有大高潮"
            ],
            "适用": "玄幻、废柴逆袭"
        },
        "2": {
            "name": "《凡人修仙传》",
            "style": "苟道流，低调谨慎",
            "核心技巧": [
                "韩立性格：能跑就跑，绝不浪",
                "资源算计：每一步都精打细算",
                "稳扎稳打：升级虽慢但步步为营",
                "隐藏实力：不到万不得已不出手"
            ],
            "适用": "修真、凡人流"
        },
        "3": {
            "name": "《诡秘之主》",
            "style": "悬疑迭起，智斗解谜",
            "核心技巧": [
                "层层谜题：每个谜题后面是更大的谜题",
                "线索公平：给读者的线索要足够",
                "角色深度：每个角色都有自己的故事",
                "世界观自洽：设定要严谨"
            ],
            "适用": "悬疑、奇幻"
        },
        "4": {
            "name": "《雪中悍刀行》",
            "style": "文青融合，人物立体",
            "核心技巧": [
                "群像塑造：每个配角都有血有肉",
                "经典台词：设计让人记住的金句",
                "情感细腻：家国情怀、兄弟情义",
                "文笔优美：场景描写有意境"
            ],
            "适用": "武侠、仙侠"
        },
        "5": {
            "name": "《诛仙》",
            "style": "情感真挚，情节感人",
            "核心技巧": [
                "三角感情：张小凡、碧瑶、田雪琪",
                "情感纠葛：爱恨情仇要真实",
                "人物成长：从懵懂少年到一代宗师",
                "悲剧色彩：有些遗憾才让人难忘"
            ],
            "适用": "仙侠、情感线"
        },
        "6": {
            "name": "《全职高手》",
            "style": "专业细节，团队配合",
            "核心技巧": [
                "专业描写：游戏机制要真实可信",
                "团队精神：不是一个人的战斗",
                "人物魅力：每个角色都有自己的粉丝",
                "热血竞技：比赛场面要燃"
            ],
            "适用": "都市、电竞"
        },
        "7": {
            "name": "《鬼吹灯》",
            "style": "盗墓探险，悬念迭起",
            "核心技巧": [
                "真实感强：具体细节增加代入感",
                "三人组配合：性格互补，各有作用",
                "探险解谜：机关、粽子、宝藏",
                "禁忌规矩：增加盗墓仪式感"
            ],
            "适用": "悬疑、探险"
        },
        "8": {
            "name": "《遮天》",
            "style": "史诗开局，格局宏大",
            "核心技巧": [
                "九龙拉棺：震撼开局定基调",
                "禁区帝坟：每个禁区都有故事",
                "天骄辈出：人物群像写好",
                "伏笔千里：前面埋后面揭"
            ],
            "适用": "玄幻、史诗"
        }
    }

    # ============================================================================
    # 交互式询问方法
    # ============================================================================

    def __init__(self):
        self.settings = {}
        self.project_path = None

    def print_header(self, title: str):
        """打印标题"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def print_option(self, key: str, option: dict, show_reference: bool = False):
        """打印选项"""
        print(f"\n  【方案{key}】{option['name']}")
        print(f"  {option['description']}")
        if "方案" in option:
            print("  具体方案:")
            for i, plan in enumerate(option["方案"], 1):
                print(f"    {i}. {plan}")
        if show_reference and "参考" in option:
            print(f"  参考: {', '.join(option['参考'])}")

    def ask_choice(self, question: str, options: dict, allow_multiple: bool = False) -> any:
        """询问选择"""
        self.print_header(question)

        for key, option in options.items():
            self.print_option(key, option, show_reference=True)

        if allow_multiple:
            print("\n  💡 提示: 可以选择多个方案，用逗号分隔，如: 1,3")
            while True:
                response = input("\n  请选择方案编号: ").strip()
                try:
                    choices = [x.strip() for x in response.split(",")]
                    if all(c in options for c in choices):
                        return choices
                except:
                    pass
                print("  请输入有效的方案编号")
        else:
            while True:
                response = input("\n  请选择方案编号: ").strip()
                if response in options:
                    return response
                print("  请输入有效的方案编号")

    def ask_input(self, question: str, default: str = "", hint: str = "") -> str:
        """询问输入"""
        print(f"\n  {question}")
        if hint:
            print(f"  💡 提示: {hint}")
        if default:
            response = input(f"  (直接回车默认: {default}): ").strip()
        else:
            response = input("  请输入: ").strip()
        return response if response else default

    def ask_confirm(self, question: str, default: bool = True) -> bool:
        """询问确认"""
        choice = "[Y/n]" if default else "[y/N]"
        while True:
            response = input(f"\n  {question} {choice}: ").strip().lower()
            if not response:
                return default
            if response in ("y", "yes"):
                return True
            if response in ("n", "no"):
                return False
            print("  请输入 y 或 n")

    # ============================================================================
    # 主流程
    # ============================================================================

    def run(self):
        """运行交互式生成"""
        self.print_header("NovelForge 交互式小说生成器")

        print("\n  本工具将引导你完成小说设定的每一步配置")
        print("  每个步骤都提供多个方案供你选择和参考")
        print("  让我们开始吧！\n")

        # Step 1: 选择小说类型
        print("\n" + "-" * 70)
        print("  【第一步】选择小说类型")
        print("-" * 70)
        novel_type_key = self.ask_choice(
            "请选择小说类型（不同类型有不同的经典开局方案）:",
            self.NOVEL_TYPES
        )
        novel_type = self.NOVEL_TYPES[novel_type_key]["name"]

        # Step 2: 选择核心冲突
        print("\n" + "-" * 70)
        print("  【第二步】选择核心冲突")
        print("-" * 70)
        print(f"  已选择类型: {novel_type}")
        print("  💡 不同冲突类型决定故事主线和爽点设计\n")

        conflict_key = self.ask_choice(
            "请选择核心冲突（这是故事的核心驱动力）:",
            self.CONFLICT_OPTIONS
        )
        conflict = self.CONFLICT_OPTIONS[conflict_key]["name"]

        # Step 3: 选择金手指
        print("\n" + "-" * 70)
        print("  【第三步】选择金手指")
        print("-" * 70)
        golden_key = self.ask_choice(
            "请选择主角的金手指（这是主角逆袭的关键）:",
            self.GOLDEN_FINGERS
        )
        golden = self.GOLDEN_FINGERS[golden_key]["name"]

        # Step 4: 选择参考风格
        print("\n" + "-" * 70)
        print("  【第四步】选择参考风格")
        print("-" * 70)
        print("  💡 可以选择多个风格进行融合，打造独特味道\n")

        style_keys = self.ask_choice(
            "请选择写作参考风格:",
            self.STYLE_REFERENCES,
            allow_multiple=True
        )

        # Step 5: 设置书名和主角
        print("\n" + "-" * 70)
        print("  【第五步】设置基础信息")
        print("-" * 70)

        title = self.ask_input(
            "请输入小说书名",
            default="星辰剑影",
            hint="一个好名字能让读者记住"
        )

        protagonist = self.ask_input(
            "请输入主角姓名",
            default="陈墨",
            hint="主角名字要响亮好记"
        )

        background = self.ask_input(
            "请输入主角背景",
            default="陈家遗孤，被灭门后流落青云宗",
            hint="描述主角的身世和来历"
        )

        # Step 6: 设置章节
        print("\n" + "-" * 70)
        print("  【第六步】设置章节参数")
        print("-" * 70)

        words = self.ask_input(
            "每章目标字数",
            default="3000",
            hint="网文一般2000-5000字一章"
        )

        chapters = self.ask_input(
            "计划总章节数",
            default="100",
            hint="百万字约330章"
        )

        # Step 7: 确认
        self.print_header("📖 小说设定确认")

        selected_styles = [self.STYLE_REFERENCES[k]["name"] for k in style_keys]
        conflict_info = self.CONFLICT_OPTIONS[conflict_key]

        print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║  书名: {title:<54} ║
  ║  类型: {novel_type:<54} ║
  ║  主角: {protagonist:<54} ║
  ║  背景: {background[:54]:<54} ║
  ║  金手指: {golden:<52} ║
  ║  核心冲突: {conflict:<50} ║
  ║  冲突核心: {conflict_info['核心'][:54]:<54} ║
  ║  参考风格: {', '.join(selected_styles)[:54]:<54} ║
  ║  每章字数: {words:<52} ║
  ║  计划章节: {chapters:<52} ║
  ╚══════════════════════════════════════════════════════════════════╝
        """)

        if not self.ask_confirm("确认以上设置？"):
            print("\n  已取消，请重新运行")
            return

        # 保存设置
        self.settings = {
            "title": title,
            "type": novel_type,
            "type_key": novel_type_key,
            "protagonist": protagonist,
            "background": background,
            "golden_finger": golden,
            "golden_key": golden_key,
            "conflict": conflict,
            "conflict_key": conflict_key,
            "styles": selected_styles,
            "style_keys": style_keys,
            "words_per_chapter": words,
            "chapter_count": chapters
        }

        # 生成小说
        self.generate_novel()

    def generate_novel(self):
        """生成小说"""
        print("\n" + "=" * 70)
        print("  开始生成小说内容")
        print("=" * 70)

        project_path = Path("novels") / self.settings["title"]
        project_path.mkdir(parents=True, exist_ok=True)
        self.project_path = project_path

        # 生成各部分
        if self.ask_confirm("\n是否生成世界观设定？"):
            content = self.generate_world_settings()
            (project_path / "settings" / "world.md").write_text(content, encoding='utf-8')
            print("  ✅ 世界观设定已保存")

        if self.ask_confirm("\n是否生成角色设定？"):
            content = self.generate_character_settings()
            (project_path / "settings" / "characters.md").write_text(content, encoding='utf-8')
            print("  ✅ 角色设定已保存")

        if self.ask_confirm("\n是否生成修炼体系？"):
            content = self.generate_system_settings()
            (project_path / "settings" / "system.md").write_text(content, encoding='utf-8')
            print("  ✅ 修炼体系已保存")

        if self.ask_confirm("\n是否生成章节大纲？"):
            content = self.generate_chapter_outline()
            (project_path / "volumes" / "volume_1" / "outline.md").write_text(content, encoding='utf-8')
            print("  ✅ 章节大纲已保存")

        if self.ask_confirm("\n是否生成第一章？"):
            content = self.generate_chapter_1()
            chapters_dir = project_path / "volumes" / "volume_1" / "chapters"
            chapters_dir.mkdir(parents=True, exist_ok=True)
            (chapters_dir / "ch_001.md").write_text(content, encoding='utf-8')
            print("  ✅ 第一章已保存")

            if self.ask_confirm("\n是否预览第一章？", default=False):
                print("\n" + "-" * 70)
                print(content)
                print("-" * 70)

        print(f"\n  ✅ 小说生成完成！")
        print(f"  📁 项目路径: {project_path}")

    def generate_world_settings(self) -> str:
        """生成世界观"""
        conflict_map = {
            "退婚流": "退婚流开局，三年之约",
            "灭门流": "灭门复仇开局，血海深仇",
            "废物流": "废物流开局，资质平庸",
            "穿越流": "穿越开局，时空转换",
            "争锋流": "宗门争斗，天才竞争",
            "逆袭流": "扮猪吃虎，隐藏身份"
        }

        golden_map = {
            "系统": "系统任务驱动，奖励兑换",
            "老爷爷": "强者传承，指导辅助",
            "神器": "上古宝物，特殊能力",
            "体质": "特殊体质，天生强大",
            "空间": "独立空间，时间流速"
        }

        return f"""# 世界观设定

## 世界概述

【{self.settings['type']}世界】

这是一个{self.settings['type']}世界，{self.NOVEL_TYPES[self.settings['type_key']]['description']}。

## 地域划分

- 中州：修仙圣地，宗门林立，灵气充沛
- 东荒：妖兽横行，危险与机遇并存
- 南疆：瘴气弥漫，毒虫肆虐
- 西漠：沙海茫茫，古城遗迹
- 北冰：冰封万里，苦寒之地

## 势力分布

1. 正道宗门 - 名门正派，传承悠久
2. 魔道势力 - 诡秘莫测，行事狠辣
3. 世俗王朝 - 王权至上，凡人国度
4. 散修联盟 - 草根势力，抱团取暖

## 核心设定

### 核心冲突
{conflict_map.get(self.settings['conflict'], '默认冲突')}

### 金手指设定
{golden_map.get(self.settings['golden_finger'], '默认金手指')}
"""

    def generate_character_settings(self) -> str:
        """生成角色设定"""
        return f"""# 角色设定

## 主角

### {self.settings['protagonist']}

- **身份**: {self.settings['background']}
- **性格**: 沉默寡言，心思细腻，外冷内热
- **目标**: 查明真相，逆袭崛起
- **金手指**: {self.settings['golden_finger']}

## 主要配角

### 苏晴雪
- 身份：宗门千金/师姐
- 性格：天真善良，有自己的主见
- 与主角关系：情感线女主

### 周长老
- 身份：宗门长老
- 性格：刚正不阿，眼光独到
- 与主角关系：伯乐，发现主角潜力

### 刘老伯
- 身份：杂役堂管事
- 性格：老实本分，心善懦弱
- 与主角关系：三年前收留主角

## 反派

### 赵无极
- 身份：天才弟子/少主
- 性格：嚣张跋扈，睚眦必报
- 与主角关系：看主角不顺眼，经常找茬

## 情感线

- 女主：善良美丽，与主角患难与共
- 暧昧：欲拒还迎，循序渐进
- 经典场景：英雄救美、日久生情
"""

    def generate_system_settings(self) -> str:
        """生成修炼体系"""
        return f"""# 修炼体系

## 修为境界

1. 炼气期（九层）- 感应灵气，打通经脉
2. 筑基期（初/中/后期）- 凝聚丹田，筑就道基
3. 金丹期 - 丹成无悔，道果初结
4. 元婴期 - 神魂出窍，寿命大增
5. 化神期 - 神魂化虚，沟通天地
6. 炼虚期 - 虚实转换，宗门底蕴
7. 合道期 - 合道天地，传说境界
8. 大乘期 - 半步飞升，凤毛麟角
9. 渡劫期 - 渡天劫，成真仙

## 参考风格

{chr(10).join([f"- {s}" for s in self.settings['styles']])}

## 功法等级

黄阶 < 玄阶 < 地阶 < 天阶 < 仙阶
"""

    def generate_chapter_outline(self) -> str:
        """生成章节大纲"""
        conflict_info = self.CONFLICT_OPTIONS[self.settings["conflict_key"]]

        outlines = {
            "1": """## 第一章 落魄少年

**核心**: 展示主角困境，金手指出现
**情节**:
- 主角在宗门最底层，被人欺负
- 被人嘲讽"{conflict}"（憋屈）
- 意外发现金手指/传承
- 被高人看中

**爽点**: 金手指出现，命运转折

---

## 第二章 拜师

**核心**: 拜入门下，开始修炼
**情节**:
- 周长老收徒，震惊众人
- 赵无极嫉妒，当众羞辱
- 主角隐忍，但展露锋芒
- 情感线铺垫

**爽点**: 众人被打脸

---

## 第三章 宗门大比

**核心**: 第一次展示实力
**情节**:
- 大比开始，主角被迫参赛
- 众人嘲笑，等着看笑话
- 主角连胜，展现实力
- 赵无极使阴招，主角反杀

**爽点**: 越级挑战，大胜""",
            "2": """## 第一章 血海深仇

**核心**: 展示灭门背景，金手指出现
**情节**:
- 回忆灭门惨案
- 主角流落他乡，隐姓埋名
- 被青云宗收留，做杂役
- 意外发现金手指

**爽点**: 金手指出现，复仇有望

---

## 第二章 隐忍

**核心**: 暗中调查，等待时机
**情节**:
- 在宗门低调行事
- 发现线索，指向仇人
- 金手指成长
- 结识盟友

**爽点**: 暗中收集证据

---

## 第三章 初次交锋

**核心**: 与仇人势力第一次冲突
**情节**:
- 仇人势力出现
- 主角被迫应战
- 金手指发威
- 身份差点暴露

**爽点**: 小试牛刀""",
            "3": """## 第一章 废物

**核心**: 展示"废物"身份
**情节**:
- 开局就被嘲讽
- 资质测试，被判定为废物
- 被人欺负，憋屈
- 金手指出现

**爽点**: 废物？不，是隐藏天才

---

## 第二章 打脸

**核心**: 第一次打脸
**情节**:
- 测试实力，展现真正天赋
- 众人震惊
- 被打脸者不服
- 被长老看中

**爽点**: 狠狠打脸

---

## 第三章 逆袭开始

**核心**: 正式逆袭
**情节**:
- 开始修炼，进步神速
- 资源争夺
- 敌对势力出手
- 主角反击

**爽点**: 越级战斗""",
            "4": """## 第一章 穿越

**核心**: 穿越到异世界
**情节**:
- 穿越醒来，发现处境
- 原主记忆涌入
- 发现金手指
- 了解世界

**爽点**: 新世界新机遇

---

## 第二章 适应

**核心**: 适应新身份
**情节**:
- 收拾原主留下的烂摊子
- 发现家族困境
- 利用现代知识解决一些问题
- 金手指开始作用

**爽点**: 用现代知识碾压古人

---

## 第三章 崛起

**核心**: 正式崛起
**情节**:
- 展现实力
- 收获第一桶金
- 结识重要人物
- 敌对势力出现

**爽点**: 快速成长""",
            "5": """## 第一章 天才竞争

**核心**: 进入竞争环境
**情节**:
- 通过选拔进入宗门
- 遇到各路天才
- 发现竞争激烈
- 金手指出现

**爽点**: 竞争开始

---

## 第二章 锋芒初露

**核心**: 展现潜力
**情节**:
- 第一次测试，表现惊人
- 天才之间的争斗
- 结识盟友
- 得罪强敌

**爽点**: 震惊众人

---

## 第三章 激烈竞争

**核心**: 竞争白热化
**情节**:
- 资源争夺
- 强敌打压
- 主角反击
- 大比开始

**爽点**: 以弱胜强""",
            "6": """## 第一章 隐藏身份

**核心**: 展示隐藏身份
**情节**:
- 表面是废物/杂役
- 实际身份惊人
- 被人看不起
- 金手指辅助

**爽点**: 扮猪吃虎

---

## 第二章 小试牛刀

**核心**: 第一次出手
**情节**:
- 被人欺负到头上
- 不得不暴露一点实力
- 震惊全场
- 引发怀疑

**爽点**: 一鸣惊人

---

## 第三章 身份危机

**核心**: 身份差点暴露
**情节**:
- 引来关注
- 被人调查
- 主角应对
- 金手指再次发威

**爽点**: 化险为夷"""
        }

        outline = outlines.get(self.settings["conflict_key"], outlines["1"])

        return f"""# 第一卷 青云宗

# 核心冲突: {conflict_info['name']}
# 冲突核心: {conflict_info['核心']}

{outline}

---

## 第四章 暗流涌动

**核心**: 危机降临
**情节**:
- 赵无极请家族出手
- 魔道中人出现
- 主角遭遇暗杀
- 神秘人相救

**悬念**: 神秘人是谁？

---

## 第五章 真相

**核心**: 真相揭示
**情节**:
- 神秘人揭示身份
- 透露主角身世
- 传授功法
- 新目标确立

**高潮**: 知道仇人是谁
"""

    def generate_chapter_1(self) -> str:
        """生成第一章"""
        protagonist = self.settings["protagonist"]
        conflict_key = self.settings["conflict_key"]

        openings = {
            "1": f"""# 第一章 落魄少年

天还没亮，{protagonist}就醒了。

不是被什么吵醒的，是习惯。

在这个地方，睡过头是要挨骂的。

他穿好那身洗得发白的灰布衫，摸黑走出杂役房。清晨的山风带着凉意，吹得他打了个哆嗦。

青云宗后山，竹林。

{protagonist}熟练地挥起柴刀。

"咔嚓"、"咔嚓"、"咔嚓"……

竹子一根接一根倒下。他的动作很稳，手上全是老茧，虎口处裂了几道口子，但他连眉头都没皱一下。

三年了。

这种日子，他已经过了三年。

---

"哟，{ protagonist}，又这么早？"

一个吊儿郎当的声音从身后传来。

{ protagonist}没回头。他知道是谁——赵元，外门弟子，专门负责"监管"他们这些杂役。

"问你话呢，聋了？"赵元一脚踹过来。

{ protagonist}侧身避开，站起身。

"元哥早。"

他的声音很平静。

赵元皱了皱眉。本来想找点乐子，但这小子跟个木头似的，怎么欺负都没反应，没劲。

"行了，今天多砍十把，少一把别想吃饭。"

说完，赵元晃晃悠悠走了。

{ protagonist}看着他的背影，眼底深处闪过一丝冷意。

不是怕。

是还没到时候。

---

{ protagonist}的背景，是宗门里大家都知道的秘密——他是个被灭门的遗孤。

十年前的那个雪夜，一切都变了。

火光冲天，惨叫四起。

他亲眼看着他爹被人一剑穿心，亲眼看着他娘跳井自尽。偌大的府邸，一夜之间化为焦土。

要不是老管家拼死相护，他早就死了。

"少爷……跑……往南边跑……青云宗……"

这是老管家最后的话。

---

"墨娃子，吃饭了。"

刘老伯端着碗热粥走过来。

"谢谢刘爷爷。"

三年来，刘老伯对他很好。在这个冰冷的宗门里，老人是为数不多让他感到温暖的人。

---

吃完饭，{ protagonist}去后山挑水。

路过一片偏僻的竹林时，他突然停下脚步。

胸口那块地方，又开始隐隐作痛了。

从三年前开始，他的胸口就经常隐隐作痛。

但今天，这股痛楚格外强烈。

他四下张望，顺着那股莫名的感应走了过去。

穿过荆棘丛，绕过巨石。

他来到了一个从未见过的地方——一处幽深的山谷。

雾气很浓，几乎看不见路。

而山谷中央的岩壁上，插着一柄剑。

一柄漆黑的、断成两截的古剑。

{ protagonist}的心脏猛地跳了一下。

"咚！"

"咚！"

"咚！"

像是擂鼓，又像是敲钟。他的血液在沸腾。

这剑……在叫我？

他慢慢走近。

就在他靠近的瞬间——

"嗡！"

*"来……"*

*"过来……"*

{ protagonist}下意识伸出手，指尖触碰到冰冷的剑身。

"轰！"

白光炸开！

然后，他昏了过去。

---

不知过了多久。

{ protagonist}悠悠转醒。

他发现自己躺在地上，那柄古剑已经黯淡无光。

"发生什么了……"

他挣扎着想坐起来，却发现脑子里多了很多东西。

一套剑法！

一套心法！

"{{{{{ protagonist}}}}，你我有缘。这传承，便赠予你了。"

声音消散。

{ protagonist}跪在原地，久久不语。

他的命运，从这一刻开始，彻底不同了。

---

"咔嚓。"

一声轻响打破了寂静。

{ protagonist}猛然回头。

只见不远处的灌木丛后，一个白发苍苍的老者正缓缓走出。

周长老！

青云宗外门三大长老之一！

"你叫什么名字？"

"{ protagonist}。"

"你可愿随我修炼？"

{ protagonist}愣住了。

"我……我愿意！"

周长老点点头，转身就走。

"明日卯时，来剑阁找我。"

{ protagonist}站在原地，心跳如雷。

"爹，娘……孩儿的命运，终于要改变了。"
"""
        }

        return openings.get(conflict_key, openings["1"])


def main():
    generator = NovelForgeInteractive()
    generator.run()


if __name__ == "__main__":
    main()
