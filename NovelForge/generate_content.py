#!/usr/bin/env python3
"""
NovelForge 交互式内容生成器
写作前必须询问操作者确认
"""

import sys
import json
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "skills"))


def ask_yes_no(question: str, default: Optional[bool] = None) -> bool:
    """询问是否确认"""
    if default is None:
        choices = "[y/n]"
    elif default is True:
        choices = "[Y/n]"
    else:
        choices = "[y/N]"

    while True:
        response = input(f"{question} {choices}: ").strip().lower()
        if not response and default is not None:
            return default
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        print("请输入 y 或 n")


def ask_choice(question: str, options: list, default: Optional[int] = None) -> int:
    """询问选择"""
    print(f"\n{question}")
    for i, option in enumerate(options, 1):
        marker = " ← 默认" if default == i else ""
        print(f"  {i}. {option}{marker}")

    while True:
        response = input("请选择 (1-{}): ".format(len(options))).strip()
        if not response and default is not None:
            return default
        try:
            choice = int(response)
            if 1 <= choice <= len(options):
                return choice
        except ValueError:
            pass
        print("请输入有效的选项编号")


def ask_input(question: str, default: Optional[str] = None) -> str:
    """询问输入"""
    prompt = f"{question}"
    if default:
        prompt += f" [{default}]"
    prompt += ": "

    response = input(prompt).strip()
    return response if response else (default or "")


def ask_multiple(question: str, options: list) -> list:
    """询问多项选择"""
    print(f"\n{question}")
    print("(输入编号，用逗号分隔，如: 1,3,5)")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        response = input("请选择: ").strip()
        if not response:
            return []
        try:
            choices = [int(x.strip()) for x in response.split(",")]
            if all(1 <= c <= len(options) for c in choices):
                return choices
        except ValueError:
            pass
        print("请输入有效的编号")


def interactive_setup():
    """交互式设置"""
    print("\n" + "=" * 60)
    print("NovelForge 交互式内容生成器")
    print("=" * 60)

    # 1. 询问小说类型
    print("\n【步骤1/8】选择小说类型")
    novel_types = [
        "玄幻（废柴逆袭、打怪升级）",
        "仙侠（修仙问道、飞升长生）",
        "都市（扮猪吃虎、打脸爽文）",
        "修真（凡人流、苟道流）",
        "武侠（江湖恩怨、侠客义气）",
        "科幻（星际探索、科技设定）",
        "悬疑（逻辑推理、层层悬念）",
        "同人（原著角色互动）"
    ]
    type_choice = ask_choice("请选择小说类型:", novel_types, 1)
    novel_type = ["xuanhuan", "xianxia", "urban", "xiuzhen", "wuxia", "kehuan", "xuanyi", "tongren"][type_choice - 1]

    # 2. 询问书名
    print("\n【步骤2/8】设置书名")
    title = ask_input("请输入书名", "星辰剑影")

    # 3. 询问主角
    print("\n【步骤3/8】设置主角")
    protagonist_name = ask_input("主角姓名", "陈墨")
    protagonist_background = ask_input("主角背景（如：废柴少爷/穿越者/遗孤）", "陈家遗孤，被灭门后流落青云宗")

    # 4. 询问金手指
    print("\n【步骤4/8】设置金手指")
    golden_finger_options = [
        "系统（任务奖励、兑换商城）",
        "老爷爷（神秘传承、辅助指导）",
        "神器（上古宝物、特殊能力）",
        "体质（特殊体质、天生强大）",
        "空间（储物空间、加速修炼）"
    ]
    golden_choice = ask_choice("主角金手指类型:", golden_finger_options, 1)
    golden_finger = ["系统", "老爷爷", "神器", "体质", "空间"][golden_choice - 1]

    # 5. 询问核心冲突
    print("\n【步骤5/8】设置核心冲突")
    conflict_options = [
        "退婚流（被退婚，三年之约）",
        "灭门流（家族被灭，复仇主线）",
        "废物流（资质平庸，逆袭崛起）",
        "穿越流（穿越异世，重新开始）",
        "争锋流（宗门争斗，天才竞争）"
    ]
    conflict_choice = ask_choice("核心冲突类型:", conflict_options, 2)
    core_conflict = ["退婚流", "灭门流", "废物流", "穿越流", "争锋流"][conflict_choice - 1]

    # 6. 询问写作风格
    print("\n【步骤6/8】选择参考风格")
    style_options = [
        "《斗破苍穹》（爽点密集，打脸干脆）",
        "《凡人修仙传》（苟道流，低调谨慎）",
        "《诡秘之主》（悬疑迭起，智斗解谜）",
        "《雪中悍刀行》（文青融合，人物立体）",
        "《诛仙》（情感真挚，情节感人）",
        "《全职高手》（专业细节，团队配合）"
    ]
    style_choice = ask_multiple("选择参考风格（可多选）", style_options)
    if not style_choice:
        style_choice = [1]

    # 7. 询问每章目标字数
    print("\n【步骤7/8】设置章节")
    words_per_chapter = ask_input("每章目标字数", "3000")
    chapter_count = ask_input("计划章节数", "100")

    # 8. 确认
    print("\n【步骤8/8】确认设置")
    print("\n" + "=" * 60)
    print("📖 小说设定确认")
    print("=" * 60)
    print(f"  书名: {title}")
    print(f"  类型: {novel_types[type_choice-1]}")
    print(f"  主角: {protagonist_name}")
    print(f"  背景: {protagonist_background}")
    print(f"  金手指: {golden_finger}")
    print(f"  核心冲突: {conflict_options[conflict_choice-1]}")
    print(f"  参考风格:")
    for idx in style_choice:
        print(f"    - {style_options[idx-1]}")
    print(f"  每章字数: {words_per_chapter}")
    print(f"  计划章节: {chapter_count}")
    print("=" * 60)

    if not ask_yes_no("确认以上设置？", True):
        print("\n已取消，请重新运行")
        sys.exit(0)

    return {
        "title": title,
        "type": novel_type,
        "protagonist": protagonist_name,
        "background": protagonist_background,
        "golden_finger": golden_finger,
        "conflict": core_conflict,
        "styles": style_choice,
        "words_per_chapter": words_per_chapter,
        "chapter_count": chapter_count
    }


def generate_novel(settings: dict):
    """根据设置生成小说"""
    print("\n开始生成小说内容...")

    project_path = Path("novels") / settings["title"]
    project_path.mkdir(parents=True, exist_ok=True)

    # 生成设定
    if ask_yes_no("\n是否生成世界观设定？", True):
        world_settings = generate_world_settings(settings)
        (project_path / "settings" / "world.md").write_text(world_settings, encoding='utf-8')
        print(f"✅ 世界观设定已保存")

    # 生成角色
    if ask_yes_no("\n是否生成角色设定？", True):
        char_settings = generate_character_settings(settings)
        (project_path / "settings" / "characters.md").write_text(char_settings, encoding='utf-8')
        print(f"✅ 角色设定已保存")

    # 生成修炼体系
    if ask_yes_no("\n是否生成修炼体系？", True):
        sys_settings = generate_system_settings(settings)
        (project_path / "settings" / "system.md").write_text(sys_settings, encoding='utf-8')
        print(f"✅ 修炼体系已保存")

    # 生成章节大纲
    if ask_yes_no("\n是否生成章节大纲？", True):
        outline = generate_chapter_outline(settings)
        (project_path / "volumes" / "volume_1" / "outline.md").write_text(outline, encoding='utf-8')
        print(f"✅ 章节大纲已保存")

    # 生成第一章
    if ask_yes_no("\n是否生成第一章内容？", True):
        print("\n正在生成第一章...")
        chapter_content = generate_chapter_content(settings)
        chapters_dir = project_path / "volumes" / "volume_1" / "chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)
        (chapters_dir / "ch_001.md").write_text(chapter_content, encoding='utf-8')
        print(f"✅ 第一章已保存")

        # 显示生成内容
        if ask_yes_no("\n是否预览第一章内容？", False):
            print("\n" + "=" * 60)
            print(chapter_content)
            print("=" * 60)

    # 生成后续章节
    if ask_yes_no("\n是否继续生成后续章节？", False):
        start_ch = ask_input("从第几章开始？", "2")
        end_ch = ask_input("到第几章结束？", start_ch)
        for ch in range(int(start_ch), min(int(end_ch), int(start_ch) + 5) + 1):
            if ask_yes_no(f"\n是否生成第{ch}章？", True):
                print(f"\n正在生成第{ch}章...")
                # 这里调用LLM生成
                content = f"# 第{ch}章\n\n（待生成）"
                (project_path / "volumes" / "volume_1" / "chapters" / f"ch_{ch:03d}.md").write_text(content, encoding='utf-8')
                print(f"✅ 第{ch}章已保存")

    print(f"\n✅ 小说生成完成！")
    print(f"   项目路径: {project_path}")


def generate_world_settings(settings: dict) -> str:
    """生成世界观"""
    type_map = {
        "xuanhuan": "玄幻",
        "xianxia": "仙侠",
        "urban": "都市",
        "xiuzhen": "修真",
        "wuxia": "武侠",
        "kehuan": "科幻"
    }
    genre = type_map.get(settings["type"], "玄幻")

    return f"""# 世界观设定

## 世界概述

【{genre}世界】弱者如蝼蚁，强者为所欲为。

## 地域划分

- 中州：修仙圣地，宗门林立
- 东荒：妖兽横行
- 南疆：瘴气弥漫
- 西漠：古城遗迹
- 北冰：苦寒之地

## 势力分布

1. 正道宗门 - 修仙圣地
2. 魔道势力 - 诡秘莫测
3. 世俗王朝 - 王权至上
4. 散修联盟 - 草根势力

## 修炼体系

炼气 → 筑基 → 金丹 → 元婴 → 化神 → 炼虚 → 合道 → 大乘 → 渡劫
"""


def generate_character_settings(settings: dict) -> str:
    """生成角色设定"""
    return f"""# 角色设定

## 主角

### {settings["protagonist"]}

- **身份**: {settings["background"]}
- **性格**: 沉默寡言，心思细腻
- **目标**: 查明真相，逆袭崛起
- **金手指**: {settings["golden_finger"]}

## 配角

### 苏晴雪
- 身份：宗门千金
- 性格：天真善良
- 作用：情感线

### 周长老
- 身份：宗门长老
- 性格：刚正不阿
- 作用：伯乐

### 反派
- 身份：待定
- 性格：嚣张跋扈
- 作用：被打脸
"""


def generate_system_settings(settings: dict) -> str:
    """生成修炼体系"""
    return """# 修炼体系

## 修为境界

1. 炼气期（九层）- 感应灵气
2. 筑基期（初/中/后期）- 凝聚丹田
3. 金丹期 - 丹成无悔
4. 元婴期 - 神魂出窍
5. 化神期 - 沟通天地
6. 炼虚期 - 宗门底蕴
7. 合道期 - 传说境界
8. 大乘期 - 半步飞升
9. 渡劫期 - 渡天劫

## 功法等级

黄阶 < 玄阶 < 地阶 < 天阶 < 仙阶
"""


def generate_chapter_outline(settings: dict) -> str:
    """生成章节大纲"""
    conflict_map = {
        "退婚流": "被未婚妻退婚，立下三年之约",
        "灭门流": "家族被灭，发誓查明真相复仇",
        "废物流": "资质平庸，被人嘲笑，逆袭崛起",
        "穿越流": "穿越到异世界，重新开始人生",
        "争锋流": "宗门大比，争夺资源"
    }
    conflict = conflict_map.get(settings["conflict"], "废物流")

    return f"""# 第一卷 大纲

## 第一章 落魄少年

**核心冲突**: {conflict}
**情节**: 主角出场，展示困境
**爽点**: 金手指出现

## 第二章 拜师

**核心冲突**: 拜入门下
**情节**: 被高人看中，收为徒弟
**爽点**: 打脸看不起自己的人

## 第三章 宗门大比

**核心冲突**: 实力展示
**情节**: 大比开始，主角展现实力
**爽点**: 越级挑战，打脸成功

## 第四章 暗流涌动

**核心冲突**: 危机降临
**情节**: 反派报复，危机出现
**悬念**: 主角如何应对？

## 第五章 传承

**核心冲突**: 真相揭示
**情节**: 获得传承，了解身世
**高潮**: 知道仇人是谁
"""


def generate_chapter_content(settings: dict) -> str:
    """生成章节内容"""
    return f"""# 第一章 落魄少年

天还没亮，{settings["protagonist"]}就醒了。

不是被什么吵醒的，是习惯。

在这个地方，睡过头是要挨骂的。

---

他穿好那身洗得发白的灰布衫，摸黑走出杂役房。清晨的山风带着凉意，吹得他打了个哆嗦。

青云宗后山，竹林。

{settings["protagonist"]}熟练地挥起柴刀。

"咔嚓"、"咔嚓"、"咔嚓"……

竹子一根接一根倒下。他的动作很稳，手上全是老茧，虎口处裂了几道口子，但他连眉头都没皱一下。

三年了。

这种日子，他已经过了三年。

---

"哟，{{{{settings['protagonist']}}}}，又这么早？"

一个吊儿郎当的声音从身后传来。

{{{{settings['protagonist']}}}}没回头。他知道是谁——赵元，外门弟子，专门负责"监管"他们这些杂役。

"问你话呢，聋了？"赵元一脚踹过来。

{{{{settings['protagonist']}}}}侧身避开，站起身。

"元哥早。"

他的声音很平静。

赵元皱了皱眉。这小子跟个木头似的，怎么欺负都没反应，没劲。

"行了，今天多砍十把，少一把别想吃饭。"

说完，赵元晃晃悠悠走了。

{{{{settings['protagonist']}}}}看着他的背影，眼底深处闪过一丝冷意。

不是怕。

是还没到时候。

---

{settings['background']}。

十年前的那个雪夜，一切都变了。

火光冲天，惨叫四起。

他亲眼看着……

（此处需要根据设定详细展开）

---

"墨娃子，吃饭了。"

刘老伯端着碗热粥走过来，浑浊的眼睛里满是慈祥。

"谢谢刘爷爷。"

三年来，刘老伯对他很好。在这个冰冷的宗门里，老人是为数不多让他感到温暖的人。

---

吃完饭，{settings['protagonist']}去后山挑水。

路过一片偏僻的竹林时，他突然停下脚步。

胸口那块地方，又开始隐隐作痛了。

从三年前开始，他的胸口就经常隐隐作痛。他不知道是什么，也不敢问人。

但今天，这股痛楚格外强烈。

{settings['protagonist']}四下张望，顺着那股莫名的感应走了过去。

穿过荆棘丛，绕过巨石。

他来到了一个从未见过的地方——一处幽深的山谷。

雾气很浓，几乎看不见路。

而山谷中央的岩壁上，插着一柄剑。

一柄漆黑的、断成两截的古剑。

{settings['protagonist']}的心脏猛地跳了一下。

"咚！"

"咚！"

"咚！"

像是擂鼓，又像是敲钟。他的血液在沸腾。

这剑……在叫我？

他慢慢走近。

近了。

更近了。

就在他靠近的瞬间——

"嗡！"

*"来……"*

*"过来……"*

{settings['protagonist']}下意识伸出手，指尖触碰到冰冷的剑身。

"轰！"

白光炸开！

然后，他昏了过去。

---

不知过了多久。

{settings['protagonist']}悠悠转醒。

他发现自己躺在地上，那柄古剑已经黯淡无光。

"发生什么了……"

他挣扎着想坐起来，却发现脑子里多了很多东西。

一套剑法！{{{{settings.get('golden_finger', '神秘')}}}}传承——

"{{{{settings['protagonist']}}}}，你我有缘。这传承，便赠予你了。"

声音消散。

{settings['protagonist']}跪在原地，久久不语。

他的命运，从这一刻开始，彻底不同了。

---

"咔嚓。"

一声轻响打破了寂静。

{settings['protagonist']}猛然回头。

周长老！

青云宗外门三大长老之一！

"你叫什么名字？"

"{{{{settings['protagonist']}}}}。"

"你可愿随我修炼？"

{{{{settings['protagonist']}}}}愣住了。

"我……我愿意！"

周长老点点头，转身就走。

"明日卯时，来剑阁找我。"

{settings['protagonist']}站在原地，心跳如雷。

"爹，娘……孩儿的命运，终于要改变了。"
"""


def main():
    settings = interactive_setup()
    generate_novel(settings)


if __name__ == "__main__":
    main()
