#!/usr/bin/env python3
"""
NovelForge 批量生成测试脚本
展示多Agent协作流程，生成100章测试小说
"""

import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "skills"))

from skills.novel_forge.novel_manager import NovelManager, NovelProject


class MultiAgentSimulator:
    """多Agent协作模拟器"""

    def __init__(self, project: NovelProject):
        self.project = project
        self.agents = {
            "architect": self._architect_agent,
            "writer": self._writer_agent,
            "auditor": self._auditor_agent,
            "reviser": self._reviser_agent
        }

    def _architect_agent(self, chapter_num: int, context: dict) -> dict:
        """建筑师Agent - 规划章节结构"""
        stage = self._get_stage(chapter_num)
        return {
            "structure": f"起({stage['start']}) -> 承({stage['transition']}) -> 转({stage['climax']}) -> 合({stage['resolution']})",
            "key_elements": stage["elements"],
            "foreshadow": stage.get("foreshadow", []),
            "word_target": random.randint(2500, 3500)
        }

    def _writer_agent(self, chapter_num: int, plan: dict, context: dict) -> str:
        """写手Agent - 生成章节内容"""
        protagonist = context.get("protagonist", "主角")
        rival = context.get("rival", "赵无极")
        sect = context.get("sect", "青云宗")
        golden = context.get("golden_finger", "神秘传承")

        stage = self._get_stage(chapter_num)
        chapter_type = stage["type"]

        templates = {
            "开篇": self._template_open,
            "修炼": self._template_training,
            "冲突": self._template_conflict,
            "机遇": self._template_opportunity,
            "高潮": self._template_climax,
            "收尾": self._template_ending,
            "过渡": self._template_transition
        }

        template_func = templates.get(chapter_type, templates["过渡"])
        return template_func(chapter_num, protagonist, rival, sect, golden, stage)

    def _auditor_agent(self, content: str) -> dict:
        """审计Agent - 质量检查"""
        issues = []
        warnings = []

        if len(content) < 2000:
            issues.append("章节过短")
        if content.count("。") < 20:
            warnings.append("对话偏少")

        return {
            "pass": len(issues) == 0,
            "score": 8.5 if len(issues) == 0 else 7.0,
            "issues": issues,
            "warnings": warnings
        }

    def _reviser_agent(self, content: str, audit: dict) -> str:
        """修订Agent - 优化内容"""
        if audit.get("score", 0) < 8.0:
            content = content.replace("说道", "沉声道")
            content = content.replace("非常", "极为")
        return content

    def _get_stage(self, chapter_num: int) -> dict:
        """根据章节号获取阶段信息"""
        if chapter_num <= 10:
            return {
                "type": "开篇", "start": "1-3", "transition": "4-6", "climax": "7-8", "resolution": "9-10",
                "elements": ["金手指觉醒", "拜入宗门", "被欺辱"]
            }
        elif chapter_num <= 25:
            return {
                "type": "修炼", "start": "11-13", "transition": "14-18", "climax": "19-21", "resolution": "22-25",
                "elements": ["苦修提升", "结识好友", "实力初显"],
                "foreshadow": ["神秘势力", "身世之谜"]
            }
        elif chapter_num <= 45:
            return {
                "type": "冲突", "start": "26-30", "transition": "31-36", "climax": "37-40", "resolution": "41-45",
                "elements": ["宗门大比", "强敌出现", "生死危机"]
            }
        elif chapter_num <= 70:
            return {
                "type": "机遇", "start": "46-50", "transition": "51-58", "climax": "59-63", "resolution": "64-70",
                "elements": ["秘境探险", "获得传承", "势力崛起"]
            }
        elif chapter_num <= 90:
            return {
                "type": "高潮", "start": "71-75", "transition": "76-82", "climax": "83-87", "resolution": "88-90",
                "elements": ["大战将至", "揭露阴谋", "终极对决"]
            }
        else:
            return {
                "type": "收尾", "start": "91-93", "transition": "94-96", "climax": "97-98", "resolution": "99-100",
                "elements": ["新危机", "突破极限", "大结局"]
            }

    def _template_open(self, ch: int, p: str, r: str, s: str, g: str, stage: dict) -> str:
        return f"""# 第{ch}章 命运的转折

天还没亮，{p}就醒了。

不是被什么吵醒的，是习惯。

在这个弱肉强食的世界里，{s}杂役峰的杂役房中，他早已习惯了天不亮就起床干活。

"咔嚓"、"咔嚓"……

{p}熟练地劈着柴，三年了，这样的日子他已经过了整整三年。

三年前的那个雪夜，他亲眼看着自己的家族被灭门。

火光冲天，惨叫四起。

要不是老管家拼死相护，他早就死在了那场浩劫之中。

"少爷……跑……往南边跑……{s}……"

老管家临死前的话，至今还回荡在他耳边。

---

"哟，废物，又这么早？"

一个阴阳怪气的声音从身后传来。

{r}的走狗——外门弟子王虎，又来刁难他了。

{p}没有说话，只是默默继续砍柴。

他的隐忍，不是懦弱。

是等待。

等待那个机会的到来。

---

就在这时，胸口那块地方又开始隐隐发热。

那是三年前他在逃亡路上捡到的一块黑色玉佩。

玉佩上的纹路诡异而神秘，每当夜深人静的时候，总会有一种奇异的力量在其中流转。

{p}知道，这里面藏着改变他命运的钥匙。

他的金手指——{g}。

只等他找到正确的方法去开启它。

"等着吧，总有一天，我会让所有人知道，谁才是真正的废物！"

{p}握紧了拳头，眼底深处闪过一丝精光。
"""

    def _template_training(self, ch: int, p: str, r: str, s: str, g: str, stage: dict) -> str:
        return f"""# 第{ch}章 修炼之路

{p}不知道自己劈了多少柴。

只知道当最后一根柴火倒下的时候，他的双臂已经酸软得几乎抬不起来。

但他没有休息。

因为真正的修炼，才刚刚开始。

---

每天深夜，当所有人都熟睡之后，{p}就会悄悄来到后山的那处隐蔽山谷。

玉佩中的{g}，终于被他初步激活了。

"呼——"

一股温热的气流从玉佩中涌出，顺着他的经脉缓缓流动。

虽然微弱，但确实存在。

这意味着，他不再是那个天生经脉堵塞的废物。

他可以修炼了！

---

"三个月了……"

{p}睁开眼，看着自己掌心那淡淡的灵气波动，嘴角露出一丝笑意。

三个月的时间，他从一个连灵气都感应不到的废物，突破到了炼气三层。

这个速度，放在那些天才弟子身上或许不值一提。

但对他来说，已经是质的飞跃。

更重要的是，他的{g}每一次运转，都会让他对修炼的理解更深一层。

"等着吧，{r}，还有那些曾经看不起我的人……"

{p}站起身，目光投向{s}主峰的方向。

"我会让你们后悔的。"

---

回到杂役房的时候，天已经快亮了。

{p}刚躺下没多久，就被一阵喧闹声吵醒。

"快起来！{s}外门大比即将开始，所有杂役弟子都可以参加！"

"只要能在外门大比中进入前一百名，就能成为外门弟子！"

{p}猛地坐起身，眼中闪过一丝精光。

机会来了！
"""

    def _template_conflict(self, ch: int, p: str, r: str, s: str, g: str, stage: dict) -> str:
        conflicts = [
            ("王师兄，这次大比，那个废物也报名了。", "哼，不知死活的东西！", "让他知道什么叫天高地厚！"),
            ("听说了吗？那个废物居然敢挑战赵师兄的权威！", "蚍蜉撼树，不自量力。", "没错！"),
            ("大比报名处，有人公然顶撞了赵师兄！", "谁这么大胆？", f"是一个杂役弟子，叫{p}。")
        ]

        c1, c2, c3 = random.choice(conflicts)

        return f"""# 第{ch}章 宗门大比

{c1}

{c2}

{c3}

消息很快传遍了整个{s}。

所有人都知道，有一个叫{p}的杂役弟子，居然在大比报名处公然顶撞了{r}。

这简直是自寻死路！

---

大比如期而至。

{s}演武场上，人山人海。

外门弟子、内门弟子、长老……无数人都来观看这场一年一度的盛会。

{p}站在参赛弟子的队伍中，显得格外突兀。

他的杂役服，在一众锦衣华服中显得格格不入。

"那是谁？怎么穿着杂役的衣服？"

"听说是今年新报名的，叫{p}。"

"杂役也敢参加大比？真是不知天高地厚。"

嘲讽声、质疑声，此起彼伏。

但{p}始终面色平静。

他的目光越过人群，直视着高台上的{r}。

---

第一轮，淘汰赛。

{p}的对手是一个炼气五层的外门弟子。

"认输吧，废物。你不是我的对手。"对手轻蔑地说道。

{p}没有说话。

他只是缓缓抬起手。

然后——

"砰！"

一掌。

仅仅一掌，对手就被轰下了擂台。

全场哗然。

"这……这怎么可能！"

"他不是废物吗？怎么会有这么强的实力！"

高台上，{r}的脸色阴沉得可怕。

"有意思……"他喃喃道，"看来我小看你了。"

但他不知道的是，这只是{p}真正实力的冰山一角。
"""

    def _template_opportunity(self, ch: int, p: str, r: str, s: str, g: str, stage: dict) -> str:
        opportunities = ["一处上古遗迹", "一位神秘老者的传承", "一枚天阶丹药", "一本失传功法"]
        opp = random.choice(opportunities)

        return f"""# 第{ch}章 秘境探险

大比之后，{p}名声大噪。

从一个被人嘲笑的废物，一跃成为{s}最耀眼的新星。

但他知道，这还远远不够。

真正的强者，是那些站在大陆巅峰的存在。

而他现在的实力，连蝼蚁都算不上。

---

这一天，{p}收到了一封密信。

信上说，在{s}后山的某处，发现了{opp}。

这可能是他突破的契机。

没有丝毫犹豫，{p}独自一人，来到了后山深处。

---

穿过层层迷雾，{p}来到了一处隐秘的山谷。

山谷中，灵气浓郁得几乎凝成了实质。

而在山谷的正中央，有一座古老的石碑。

石碑上刻满了晦涩难懂的符文，散发着淡淡的光芒。

{p}走近，伸手触碰石碑。

"轰——"

刹那间，一股浩瀚的信息涌入他的脑海。

那是{g}的第二层功法！

"哈哈哈……果然是天选之人！"

一个苍老的声音在他脑海中响起。

"这传承，终于等到你了……"

原来，这竟然是上古大能的墓穴！

而{p}，正是被选中的传承者！

---

离开秘境后，{p}的实力突飞猛进。

炼气七层、炼气八层、炼气九层……

短短一个月，他就突破了炼气巅峰，达到了筑基初期！

这个速度，简直骇人听闻。

但{p}知道，他的目标远不止于此。

他的{g}告诉他，这个世界远比他想象的要大。

而他的仇人，也远比他想象的要强大。

"等着吧，属于我的时代，即将来临！"
"""

    def _template_climax(self, ch: int, p: str, r: str, s: str, g: str, stage: dict) -> str:
        return f"""# 第{ch}章 惊天大战

夜幕降临，{s}笼罩在一片肃杀之气中。

今日，正是{p}与{r}约战之日。

消息早已传遍了整个修炼界。

无数高手从四面八方赶来，只为一睹这场巅峰对决。

---

"{p}，你以为突破筑基就能与我抗衡？"

{r}立于高空之上，俯视着下方的{p}。

"今天，我会让你知道，什么叫真正的天才！"

说罢，{r}出手了。

恐怖的灵气化作一道剑芒，直取{p}的性命。

这是筑基巅峰的一击，足以灭杀同阶的任何对手。

---

但{p}只是淡淡一笑。

"就这？"

他缓缓抬手。

刹那间，一道璀璨的剑光从他掌心飞出。

那是{g}的终极奥义——

一剑破万法！

"轰！！！"

两股恐怖的力量在空中碰撞，爆发出惊天动地的巨响。

整个{s}都在颤抖。

---

当烟尘散去，所有人都惊呆了。

{r}，竟然败了！

{r}浑身浴血，狼狈地躺在深坑之中。

而{p}，负手而立，衣袂飘飘，毫发无损。

"你……你怎么可能这么强！"{r}不可置信地嘶吼。

{p}居高临下地看着他，眼中没有丝毫波动。

"我说过，总有一天，我会让你后悔。"

"现在，后悔了吗？"
"""

    def _template_ending(self, ch: int, p: str, r: str, s: str, g: str, stage: dict) -> str:
        return f"""# 第{ch}章 新的征程

{r}的落败，在修炼界引起了轩然大波。

曾经那个被所有人嘲笑的废物，如今已经成长为让所有人都仰望的存在。

但{p}知道，这只是一个开始。

---

"根据我得到的线索，灭我满门的幕后黑手，远比我想象的要强大。"

{p}站在{s}最高处，眺望远方。

"中州圣地……等着我。"

那里，是他仇人所在的地方。

也是他踏上巅峰的下一站。

---

收拾好行装，{p}告别了{s}的师兄弟们。

"保重，{p}师兄！"

"一定要活着回来！"

"下次见面，我要和你喝到天亮！"

{p}微微一笑，转身离去。

他的背影，渐渐消失在夕阳的余晖中。

但没有人知道，在那遥远的中州，一场更大的风暴正在酝酿。

而{p}的{g}，也在这一路上不断觉醒，变得越来越强大。

"总有一天，我会站在这个世界的巅峰。"

"而在那之前，所有的苦难，都只是磨砺。"

远处，传来{p}低沉而坚定的声音。

新的征程，正式开始。
"""

    def _template_transition(self, ch: int, p: str, r: str, s: str, g: str, stage: dict) -> str:
        return f"""# 第{ch}章 暗流涌动

夕阳西下，{s}的钟声悠悠响起。

{p}站在自己的小院中，静静地看着天边的晚霞。

这一路走来，他已经不再是当初那个任人欺凌的废物。

但他并没有因此骄傲自满。

因为他知道，这个世界很大。

比他强大的人，还有很多很多。

---

"咚咚咚——"

敲门声响起。

"师兄，有你的信。"

{p}接过信，展开一看，眉头微微一皱。

信上说，在{s}北方的幽冥山脉中，出现了一处上古遗迹。

遗迹中，似乎藏有{g}的秘密。

"有意思……"

{p}眼中闪过一丝精光。

看来，又该出发了。
"""

    def generate_chapter(self, chapter_num: int) -> dict:
        """生成单个章节 - 多Agent协作"""
        print(f"\n  🔄 第{chapter_num}章生成中...")

        context = {
            "protagonist": "陈墨",
            "rival": "赵无极",
            "sect": "青云宗",
            "golden_finger": "星辰剑典"
        }

        print(f"    ├─ 🏗️ 建筑师Agent: 规划章节结构")
        plan = self._architect_agent(chapter_num, context)

        print(f"    ├─ ✍️ 写手Agent: 生成章节内容")
        content = self._writer_agent(chapter_num, plan, context)

        print(f"    ├─ 🔍 审计Agent: 质量检查")
        audit = self._auditor_agent(content)

        if not audit["pass"]:
            print(f"    │  ⚠️ 发现问题: {audit['issues']}")
            print(f"    ├─ 🔧 修订Agent: 优化内容")
            content = self._reviser_agent(content, audit)

        word_count = len(content)
        print(f"    └─ ✅ 完成! (字数: {word_count})")

        return {
            "chapter_num": chapter_num,
            "title": f"第{chapter_num}章",
            "content": content,
            "word_count": word_count,
            "audit_score": audit["score"]
        }


def run_batch_test(num_chapters: int = 100):
    """运行批量测试"""
    print("=" * 70)
    print("  NovelForge 多Agent协作 100章批量生成测试")
    print("=" * 70)

    project_path = Path("novels/星辰剑影_test")
    project_path.mkdir(parents=True, exist_ok=True)

    project = NovelProject(
        title="星辰剑影",
        genre="玄幻",
        synopsis="一个被灭门的少年，意外获得上古传承，踏上一条逆天改命的修仙之路",
        target_chapters=100,
        target_words_per_chapter=3000,
        created_at=datetime.now().isoformat()
    )
    project.project_path = project_path

    NovelManager._create_directory_structure(project_path)
    NovelManager._create_initial_files(project_path, project)

    print(f"\n📚 项目已创建: {project.title}")
    print(f"   路径: {project_path}")
    print(f"   目标: {num_chapters}章\n")

    simulator = MultiAgentSimulator(project)

    print("=" * 70)
    print("  开始生成章节...")
    print("=" * 70)

    start_time = time.time()
    total_words = 0
    scores = []

    for ch in range(1, num_chapters + 1):
        result = simulator.generate_chapter(ch)

        ch_path = project_path / "volumes/volume_1/chapters"
        ch_path.mkdir(parents=True, exist_ok=True)

        with open(ch_path / f"ch_{ch:03d}.md", 'w', encoding='utf-8') as f:
            f.write(result["content"])

        total_words += result["word_count"]
        scores.append(result["audit_score"])

        if ch % 10 == 0:
            elapsed = time.time() - start_time
            print(f"\n  📊 进度: {ch}/{num_chapters} | 已生成: {total_words:,}字 | 耗时: {elapsed:.1f}秒")
            print("-" * 70)

    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("  ✅ 生成完成!")
    print("=" * 70)
    print(f"\n  📈 统计:")
    print(f"     总章节: {num_chapters}")
    print(f"     总字数: {total_words:,}")
    print(f"     平均字数: {total_words // num_chapters:,}")
    print(f"     平均评分: {sum(scores) / len(scores):.1f}")
    print(f"     总耗时: {elapsed:.1f}秒")
    print(f"     生成速度: {num_chapters / elapsed:.1f}章/秒")
    print(f"\n  📁 输出路径: {project_path}/volumes/volume_1/chapters")

    return project_path


if __name__ == "__main__":
    run_batch_test(100)
