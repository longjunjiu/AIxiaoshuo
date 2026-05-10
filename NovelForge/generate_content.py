#!/usr/bin/env python3
"""
NovelForge 完整交互式小说生成系统
参考十大经典网文写作技巧
支持：退婚流、灭门流、废物流、穿越流、争锋流、逆袭流
"""

import os
import sys
import json
import time
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "skills"))

from skills.novel_forge.utils.llm_client import LLMClient
from skills.novel_forge.rules.classic_novels import get_full_novel_writing_prompt


class StoryType(Enum):
    TUIHUN = "tuihun"
    MIEMEN = "miemen"
    FEILIU = "feiliu"
    CHUANYUE = "chuanyue"
    ZHENGFENG = "zhengfeng"
    NIXI = "nixi"


@dataclass
class CharacterProfile:
    name: str
    age: int
    personality: str
    background: str
    goal: str
    golden_finger: Optional[str] = None
    relationship: Dict[str, str] = field(default_factory=dict)


@dataclass
class WorldSetting:
    name: str
    genre: str
    power_system: str
    main_factions: List[str] = field(default_factory=list)
    geography: str = ""
    history: str = ""


@dataclass
class ChapterPlan:
    chapter_num: int
    title: str
    core_event: str
    conflict: str
    climax: str
    shuangdian: str
    hook: str
    characters: List[str] = field(default_factory=list)
    location: str = ""
    tone: str = ""


@dataclass
class NovelProject:
    title: str
    author: str
    genre: str
    story_type: StoryType
    protagonist: CharacterProfile
    world: WorldSetting
    chapters: List[ChapterPlan] = field(default_factory=list)
    target_chapters: int = 100
    current_chapter: int = 0


CLASSIC_WRITING_PROMPT = """
【十大经典网文写作技巧 - 深度学习】

《斗破苍穹》核心技巧：
- 三年之约：明确目标，读者有期待
- 退婚开局：冲突强，观众有共鸣
- 憋屈→爆发：憋得越久，爆得越爽
- 打脸干脆：不要拖泥带水
- 升级异象：每次突破都有天地异象
- 扮猪吃虎：低调装逼最爽

《凡人修仙传》核心技巧：
- 苟道精髓：不浪、不惹事、但不怕事
- 资源积累：每一步都有收获
- 低调行事：隐藏实力扮猪吃虎
- 稳扎稳打：升级慢热但扎实
- 关键战斗：以弱胜强，靠智取

《诡秘之主》核心技巧：
- 层层悬念：每章都要有谜
- 世界观自洽：设定要完美闭环
- 智斗精彩：斗智斗勇
- 扮演法则：能力越大越要伪装
- 细节伏笔：草蛇灰线，伏脉千里

《雪中悍刀行》核心技巧：
- 群像塑造：每个角色都有故事
- 经典台词：天不生我李淳罡
- 文笔优美：意境深远
- 兄弟情义：有血有肉
- 江湖庙堂：格局宏大

《遮天》核心技巧：
- 九龙拉棺：史诗级开局
- 世界观宏大：宇宙星空
- 荒古圣体：逆天改命
- 帝路争锋：群雄逐鹿
- 伏笔大师：草蛇灰线

《仙逆》核心技巧：
- 顺为凡逆则仙：核心主题
- 为一人逆天：执念驱动
- 凡人流极致：稳扎稳打
- 极境突破：与众不同
- 千年等待：情感至深

《诛仙》核心技巧：
- 情感主线：三段感情纠葛
- 天地不仁：主题深刻
- 人物立体：非黑即白
- 正魔对立：立场冲突
- 悲剧色彩：爱恨交织

《全职高手》核心技巧：
- 专业细节：真实可信
- 团队配合：不是一个人的战斗
- 比赛节奏：紧张刺激
- 人物鲜明：各有特点
- 成长蜕变：从谷底到巅峰

《紫川》核心技巧：
- 幽默与严肃：完美结合
- 群像写法：每个角色都出彩
- 战争描写：大场面精彩
- 反派魅力：不是纯粹邪恶
- 悲剧深刻：动人心魄

【黄金三章法则】

第一章必须完成：
1. 主角出场，让读者认识
2. 抛出核心冲突（退婚/灭门/废物流）
3. 金手指出现或埋下伏笔
4. 章尾留悬念钩子

第二章必须完成：
1. 金手指展示
2. 第一次小试牛刀
3. 建立敌人/目标
4. 埋下更大伏笔

第三章必须完成：
1. 第一个小高潮
2. 解决或部分解决开局冲突
3. 展示主角潜力
4. 建立更大目标

【开局炸弹库】

1. 退婚炸弹
   - 未婚妻当众退婚
   - 主角被嘲讽废物
   - 三年之约立下

2. 灭门炸弹
   - 家族被灭
   - 父母惨死
   - 主角幸存

3. 废物流炸弹
   - 觉醒仪式失败
   - 被测出废物天赋
   - 众人嘲笑

4. 穿越炸弹
   - 穿越到异世界
   - 继承原身记忆
   - 面临困境

5. 逆袭炸弹
   - 最低谷时觉醒
   - 获得上古传承
   - 命运转折

【爽点设计】

小爽点（每章）：
- 打脸成功
- 装逼成功
- 收获资源
- 实力提升

中爽点（每卷）：
- 击败强敌
- 势力扩张
- 情感突破
- 身份揭露

大爽点（全书）：
- 复仇成功
- 登顶巅峰
- 有情人终成眷属
- 世界真相揭露

【语言风格要求】

✅ 好的写法：
- "少爷，你醒了？"清脆的声音传来
- 他攥紧拳头，指节发白
- "你这废物也配？"主角冷笑

❌ 禁止的写法：
- "眼中闪过一丝坚定"
- "缓缓地站起身来"
- "天空中乌云密布，仿佛在诉说着什么"
- 大段环境描写开头

【章节结构公式】

1. 开局（前300字）：
   扔炸弹、冲突、危机

2. 发展（中间部分）：
   战斗、对话、推进

3. 高潮（章中段）：
   决战、爆发、转折

4. 结尾（后200字）：
   结果、悬念、新伏笔

请严格按照以上技巧创作。
"""


class NovelWriter:
    """完整的小说写作系统"""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client
        self.project: Optional[NovelProject] = None
        self.output_dir = Path("novels")
    
    def create_project(
        self,
        title: str,
        genre: str,
        story_type: StoryType,
        protagonist: CharacterProfile,
        world: WorldSetting,
        target_chapters: int = 100
    ) -> NovelProject:
        """创建新项目"""
        self.project = NovelProject(
            title=title,
            author="AI",
            genre=genre,
            story_type=story_type,
            protagonist=protagonist,
            world=world,
            target_chapters=target_chapters
        )
        self._create_directories()
        self._save_project()
        return self.project
    
    def _create_directories(self):
        """创建项目目录"""
        if not self.project:
            return
        
        safe_title = self._sanitize_filename(self.project.title)
        self.output_dir = Path("novels") / safe_title
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        (self.output_dir / "chapters").mkdir(exist_ok=True)
        (self.output_dir / "settings").mkdir(exist_ok=True)
        (self.output_dir / "memory").mkdir(exist_ok=True)
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名"""
        import re
        return re.sub(r'[<>:"/\\|?*]', '', name)
    
    def _save_project(self):
        """保存项目"""
        if not self.project:
            return
        
        config = {
            "title": self.project.title,
            "author": self.project.author,
            "genre": self.project.genre,
            "story_type": self.project.story_type.value,
            "protagonist": {
                "name": self.project.protagonist.name,
                "age": self.project.protagonist.age,
                "personality": self.project.protagonist.personality,
                "background": self.project.protagonist.background,
                "goal": self.project.protagonist.goal,
                "golden_finger": self.project.protagonist.golden_finger
            },
            "world": {
                "name": self.project.world.name,
                "genre": self.project.world.genre,
                "power_system": self.project.world.power_system,
                "main_factions": self.project.world.main_factions,
                "geography": self.project.world.geography,
                "history": self.project.world.history
            },
            "target_chapters": self.project.target_chapters,
            "current_chapter": self.project.current_chapter
        }
        
        with open(self.output_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    def plan_chapter(self, chapter_num: int, guidance: str = "") -> ChapterPlan:
        """规划单章大纲"""
        if not self.project:
            raise ValueError("请先创建项目")
        
        prompt = self._build_chapter_plan_prompt(chapter_num, guidance)
        
        if self.llm:
            try:
                response = self.llm.chat(
                    messages=[{"role": "user", "content": prompt}],
                    system=CLASSIC_WRITING_PROMPT,
                    temperature=0.8,
                    max_tokens=2000
                )
                plan = self._parse_chapter_plan(response.content, chapter_num)
            except Exception as e:
                plan = self._get_fallback_plan(chapter_num)
        else:
            plan = self._get_fallback_plan(chapter_num)
        
        if len(self.project.chapters) >= chapter_num:
            self.project.chapters[chapter_num - 1] = plan
        else:
            self.project.chapters.append(plan)
        
        self.project.current_chapter = chapter_num
        self._save_project()
        
        return plan
    
    def _build_chapter_plan_prompt(self, chapter_num: int, guidance: str) -> str:
        """构建章节规划提示词"""
        protagonist = self.project.protagonist
        world = self.project.world
        story_type = self.project.story_type.value
        
        prev_summary = ""
        if chapter_num > 1 and len(self.project.chapters) >= chapter_num - 1:
            prev = self.project.chapters[chapter_num - 2]
            prev_summary = f"上章：{prev.title}，核心事件：{prev.core_event}"
        
        prompt = f"""请为《{self.project.title}》第{chapter_num}章设计详细大纲。

## 作品信息
- 题材：{self.project.genre}
- 流派：{story_type}
- 目标字数：2500-3000字

## 主角信息
- 姓名：{protagonist.name}
- 年龄：{protagonist.age}
- 性格：{protagonist.personality}
- 背景：{protagonist.background}
- 金手指：{protagonist.golden_finger or '待设定'}

## 世界观
- 世界名称：{world.name}
- 力量体系：{world.power_system}
- 主要势力：{', '.join(world.main_factions)}

## 前章回顾
{prev_summary}

{f"## 作者指导\n{guidance}\n" if guidance else ""}

## 输出要求

请按以下JSON格式输出：
```json
{{
    "title": "章节标题",
    "core_event": "本章核心事件（50字）",
    "conflict": "主要冲突（50字）",
    "climax": "高潮设计（100字）",
    "shuangdian": "爽点设计（50字）",
    "hook": "章尾钩子（50字）",
    "characters": ["主角", "需要出场的角色列表"],
    "location": "主要场景",
    "tone": "本章基调"
}}
```

注意：
1. 第1章必须扔出"开局炸弹"
2. 每章必须有冲突
3. 爽点设计要明确
4. 章尾必须留悬念
"""
        return prompt
    
    def _parse_chapter_plan(self, response: str, chapter_num: int) -> ChapterPlan:
        """解析章节规划响应"""
        import re
        import json
        
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return ChapterPlan(
                    chapter_num=chapter_num,
                    title=data.get('title', f'第{chapter_num}章'),
                    core_event=data.get('core_event', ''),
                    conflict=data.get('conflict', ''),
                    climax=data.get('climax', ''),
                    shuangdian=data.get('shuangdian', ''),
                    hook=data.get('hook', ''),
                    characters=data.get('characters', []),
                    location=data.get('location', ''),
                    tone=data.get('tone', '热血')
                )
            except json.JSONDecodeError:
                pass
        
        return self._get_fallback_plan(chapter_num)
    
    def _get_fallback_plan(self, chapter_num: int) -> ChapterPlan:
        """备用大纲"""
        plans = {
            1: {
                "title": "灭门之夜",
                "core_event": "家族被神秘势力灭门，主角幸存",
                "conflict": "仇人追杀，生死危机",
                "climax": "父母惨死，主角被逼入绝境",
                "shuangdian": "危急时刻，金手指觉醒",
                "hook": "神秘老者是谁？仇人为何灭门？"
            },
            2: {
                "title": "绝境求生",
                "core_event": "主角逃亡途中，偶得传承",
                "conflict": "伤势严重，敌人追兵",
                "climax": "在悬崖边获得上古剑典",
                "shuangdian": "金手指展现威力",
                "hook": "传承的真正来历是什么？"
            },
            3: {
                "title": "初入宗门",
                "core_event": "主角拜入宗门，开始修炼",
                "conflict": "资质被质疑，遭受嘲笑",
                "climax": "修炼速度震惊众人",
                "shuangdian": "打脸嘲讽者",
                "hook": "宗门里的师姐为何关注主角？"
            }
        }
        
        default_plan = plans.get(chapter_num, {
            "title": f"第{chapter_num}章",
            "core_event": "剧情推进，主角成长",
            "conflict": "新的挑战和敌人",
            "climax": "战斗高潮",
            "shuangdian": "实力提升",
            "hook": "悬念留白"
        })
        
        return ChapterPlan(
            chapter_num=chapter_num,
            **default_plan,
            characters=[self.project.protagonist.name] if self.project else ["主角"],
            location="待定",
            tone="热血"
        )
    
    def generate_chapter(self, chapter_num: int) -> str:
        """生成章节内容"""
        if not self.project:
            raise ValueError("请先创建项目")
        
        plan = self.plan_chapter(chapter_num)
        prompt = self._build_chapter_content_prompt(plan, chapter_num)
        
        if self.llm:
            try:
                response = self.llm.chat(
                    messages=[{"role": "user", "content": prompt}],
                    system=CLASSIC_WRITING_PROMPT,
                    temperature=0.85,
                    max_tokens=4000
                )
                content = self._post_process_content(response.content, plan)
            except Exception as e:
                content = self._get_fallback_content(plan)
        else:
            content = self._get_fallback_content(plan)
        
        self._save_chapter(chapter_num, plan.title, content)
        
        return content
    
    def _build_chapter_content_prompt(self, plan: ChapterPlan, chapter_num: int) -> str:
        """构建章节内容提示词"""
        protagonist = self.project.protagonist
        world = self.project.world
        
        prev_content = ""
        if chapter_num > 1:
            ch_path = self.output_dir / "chapters" / f"ch_{chapter_num-1:03d}.md"
            if ch_path.exists():
                with open(ch_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    prev_content = ''.join(lines[min(5, len(lines)):min(20, len(lines))])
        
        prompt = f"""请创作《{self.project.title}》第{chapter_num}章。

## 章节大纲
- 标题：{plan.title}
- 核心事件：{plan.core_event}
- 主要冲突：{plan.conflict}
- 高潮设计：{plan.climax}
- 爽点：{plan.shuangdian}
- 章尾钩子：{plan.hook}

## 主角信息
- 姓名：{protagonist.name}
- 年龄：{protagonist.age}岁
- 性格：{protagonist.personality}
- 背景：{protagonist.background}
- 金手指：{protagonist.golden_finger or '神秘传承'}

## 世界观
- 世界：{world.name}
- 力量体系：{world.power_system}
- 主要势力：{', '.join(world.main_factions)}

## 出场角色
{', '.join(plan.characters)}

## 主要场景
{plan.location}

## 本章基调
{plan.tone}

{f"## 前文承接\n{prev_content}\n" if prev_content else ""}

## 写作要求

1. 【开局炸弹】前300字必须扔出"炸弹"——冲突、危机、悬念
2. 【黄金三章】每章必须有冲突、有推进、有期待
3. 【爽点设计】根据题材设计适当的爽点（打脸、升级、装逼等）
4. 【悬念钩子】章尾留悬念，让读者想追更
5. 【对话自然】对话口语化，符合人物性格
6. 【动作描写】用动作和表情传达情绪，不直接写心理
7. 【节奏把控】高潮部分节奏快，过渡部分不拖沓

直接输出正文，不要输出任何解释。
"""
        return prompt
    
    def _post_process_content(self, content: str, plan: ChapterPlan) -> str:
        """后处理内容"""
        lines = content.strip().split('\n')
        
        title = plan.title
        for line in lines[:5]:
            if line.startswith('#'):
                title = line.lstrip('#').strip()
                break
        
        processed = [f"# {title}\n\n"]
        
        skip_headers = {'#', '##', '章节', '标题', '【', '】'}
        started = False
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if started:
                    processed.append(line)
                continue
            
            if not started and not any(stripped.startswith(h) for h in skip_headers):
                if len(stripped) > 10 or any(c in stripped for c in '，。！？""''""'):
                    started = True
            
            if started:
                processed.append(line)
        
        return '\n'.join(processed)
    
    def _get_fallback_content(self, plan: ChapterPlan) -> str:
        """备用内容"""
        return f"""# {plan.title}

（系统提示：需要配置LLM才能生成完整内容）

章节要求：
- 核心事件：{plan.core_event}
- 主要冲突：{plan.conflict}
- 爽点设计：{plan.shuangdian}

请配置API密钥后重新生成。
"""
    
    def _save_chapter(self, chapter_num: int, title: str, content: str):
        """保存章节"""
        ch_path = self.output_dir / "chapters" / f"ch_{chapter_num:03d}.md"
        with open(ch_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def batch_generate(self, start: int, end: int):
        """批量生成"""
        for ch in range(start, end + 1):
            print(f"正在生成第{ch}章...")
            try:
                content = self.generate_chapter(ch)
                print(f"  ✅ 第{ch}章完成 ({len(content)}字)")
            except Exception as e:
                print(f"  ❌ 第{ch}章失败: {e}")
            time.sleep(1)


def interactive_setup() -> tuple:
    """交互式设置"""
    print("\n" + "="*60)
    print("  NovelForge - 交互式小说创作系统")
    print("="*60)
    
    print("\n📚 请选择小说流派：")
    print("  1. 退婚流 - 经典打脸爽文")
    print("  2. 灭门流 - 绝境逆袭复仇")
    print("  3. 废物流 - 扮猪吃老虎")
    print("  4. 穿越流 - 异界重生")
    print("  5. 争锋流 - 天才竞争")
    print("  6. 逆袭流 - 小人物崛起")
    
    story_types = {
        "1": StoryType.TUIHUN,
        "2": StoryType.MIEMEN,
        "3": StoryType.FEILIU,
        "4": StoryType.CHUANYUE,
        "5": StoryType.ZHENGFENG,
        "6": StoryType.NIXI
    }
    
    choice = input("\n请输入选项 (1-6): ").strip()
    story_type = story_types.get(choice, StoryType.TUIHUN)
    
    print("\n📝 请输入小说信息：")
    title = input("  书名: ").strip() or "逆天改命"
    genre = input("  题材 (默认: 玄幻): ").strip() or "玄幻"
    protagonist_name = input("  主角姓名: ").strip() or "叶尘"
    
    protagonist = CharacterProfile(
        name=protagonist_name,
        age=18,
        personality="外冷内热、有仇必报",
        background="家族被灭的少年",
        goal="复仇变强",
        golden_finger="上古剑典传承"
    )
    
    world = WorldSetting(
        name="玄元大陆",
        genre=genre,
        power_system="炼气、筑基、金丹、元婴、出窍、分神、合体、大乘、渡劫",
        main_factions=["青云宗", "天魔教", "皇室", "世家"],
        geography="东荒、西域、南蛮、北域、中州",
        history="万年修仙史"
    )
    
    target = input("  目标章节数 (默认: 100): ").strip()
    target_chapters = int(target) if target.isdigit() else 100
    
    return title, genre, story_type, protagonist, world, target_chapters


def main():
    """主函数"""
    print("\n" + "="*60)
    print("  NovelForge - 交互式小说创作系统")
    print("="*60)
    
    print("\n🤖 正在初始化...")
    
    llm_client = None
    api_key = os.getenv("NVIDIA_API_KEY") or os.getenv("OPENAI_API_KEY")
    
    if api_key:
        try:
            from dataclasses import dataclass
            @dataclass
            class Config:
                llm_provider: str = "nvidia" if "NVIDIA" in str(os.environ) else "openai"
                api_key: str = api_key
                base_url: str = ""
                model: str = "meta/llama-3.1-70b-instruct"
                temperature: float = 0.7
                max_tokens: int = 4096
            
            config = Config()
            llm_client = LLMClient(config)
            print("  ✅ LLM客户端已连接")
        except Exception as e:
            print(f"  ⚠️ LLM连接失败: {e}")
            print("  📝 将使用备用模式")
    else:
        print("  ⚠️ 未检测到API密钥")
        print("  📝 将使用备用模式（功能受限）")
    
    writer = NovelWriter(llm_client)
    
    print("\n" + "-"*60)
    print("  请选择操作：")
    print("  1. 创建新小说项目")
    print("  2. 从配置文件加载")
    print("  3. 快速生成10章测试")
    print("  4. 继续生成")
    print("-"*60)
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        title, genre, story_type, protagonist, world, target = interactive_setup()
        
        writer.create_project(
            title=title,
            genre=genre,
            story_type=story_type,
            protagonist=protagonist,
            world=world,
            target_chapters=target
        )
        
        print(f"\n✅ 项目 '{title}' 创建成功！")
        
        print("\n" + "-"*60)
        print("  请选择生成方式：")
        print("  1. 生成单章")
        print("  2. 批量生成")
        print("  3. 交互式逐章生成")
        print("-"*60)
        
        gen_choice = input("\n请输入选项: ").strip()
        
        if gen_choice == "1":
            ch = int(input("请输入章节号: ").strip() or "1")
            content = writer.generate_chapter(ch)
            print(f"\n✅ 第{ch}章生成完成！")
            print(f"📁 保存位置: {writer.output_dir}/chapters/ch_{ch:03d}.md")
        elif gen_choice == "2":
            start = int(input("起始章节: ").strip() or "1")
            end = int(input("结束章节: ").strip() or "10")
            writer.batch_generate(start, end)
        elif gen_choice == "3":
            ch = writer.project.current_chapter + 1 if writer.project.current_chapter else 1
            while True:
                print(f"\n📝 第{ch}章")
                guidance = input("  输入本章指导 (直接回车使用默认): ").strip()
                content = writer.generate_chapter(ch)
                print(f"  ✅ 完成 ({len(content)}字)")
                
                if ch >= (writer.project.target_chapters if writer.project else 10):
                    break
                
                cont = input("\n是否继续生成下一章? (y/n): ").strip().lower()
                if cont != 'y':
                    break
                ch += 1
    
    elif choice == "3":
        print("\n🚀 开始快速生成测试...")
        
        writer.create_project(
            title="星辰剑影",
            genre="玄幻",
            story_type=StoryType.MIEMEN,
            protagonist=CharacterProfile(
                name="陈墨",
                age=18,
                personality="沉稳冷静、心思缜密",
                background="陈家少主，家族被灭",
                goal="查明真相，复仇雪恨",
                golden_finger="星辰剑典"
            ),
            world=WorldSetting(
                name="玄元大陆",
                genre="玄幻",
                power_system="炼体、炼气、筑基、金丹、元婴",
                main_factions=["青云宗", "天魔宫", "皇室"],
                geography="东域、中州、西域",
                history="万年修仙文明"
            ),
            target_chapters=10
        )
        
        writer.batch_generate(1, 10)
        print(f"\n✅ 测试生成完成！")
        print(f"📁 输出目录: {writer.output_dir}")
    
    else:
        print("请先创建项目或配置API密钥")


if __name__ == "__main__":
    main()
