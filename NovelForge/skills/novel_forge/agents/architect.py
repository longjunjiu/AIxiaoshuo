"""
建筑师机器人 - 规划小说结构和章节大纲
参考十大经典网文结构设计
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class OutlineContext:
    """大纲规划上下文"""
    novel_title: str
    genre: str
    tone: str
    target_word_count: int
    chapter_count: int


class ArchitectAgent:
    """
    建筑师机器人
    
    参考十大经典网文结构设计：
    - 《斗破苍穹》- 废柴逆袭，三年之约
    - 《凡人修仙传》- 凡人流，稳扎稳打
    - 《诡秘之主》- 层层悬念，智斗解谜
    - 《雪中悍刀行》- 人物群像，江湖情义
    - 《诛仙》- 情感主线，三角恋
    """
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def get_system_prompt(self) -> str:
        return """你是一位顶尖网络小说大纲规划师，精通网文结构设计。

【十大经典网文结构参考】

《斗破苍穹》结构：
- 开局：废柴被退婚，三年之约立下
- 发展：升级打怪，获得异火
- 高潮：三年期满，约战成功
- 结局：成为斗帝，击败魂族
- 核心节奏：憋屈→爆发→升级→更强的敌人→再爆发

《凡人修仙传》结构：
- 开局：韩立入门派，获得小绿瓶
- 发展：猥琐发育，到处收集资源
- 高潮：越阶战斗，以弱胜强
- 核心节奏：资源积累→境界提升→遇到危机→化解危机

《诡秘之主》结构：
- 开局：穿越到异世界，成为非凡者
- 发展：升级序列，解谜历史
- 高潮：对抗邪神，拯救世界
- 核心节奏：解谜→升级→新的谜团→更大的谜团

《雪中悍刀行》结构：
- 开局：北凉世子纨绔，父死母亡
- 发展：江湖游历，结交豪杰
- 高潮：凉莽大战，为国捐躯
- 核心节奏：个人成长→家国情怀→悲剧英雄

《诛仙》结构：
- 开局：张小凡入门青云
- 发展：三段感情，正魔之争
- 高潮：碧瑶挡剑，陆雪琪表白
- 核心节奏：修仙+爱情，虐心虐身

【网文结构公式】

第一章（开局章）：
- 建立主角处境
- 抛出核心冲突
- 埋下悬念钩子
- 300字内扔炸弹

第二章（中局章）：
- 金手指出现
- 初步展示潜力
- 埋下更大伏笔

第三章（爆发章）：
- 第一个小高潮
- 解决开局冲突（或部分解决）
- 留下更大悬念

【章节大纲要素】

每个章节大纲需要包含：
1. 章节核心事件
2. 冲突/矛盾
3. 情感转折
4. 悬念/伏笔
5. 爽点设计

【卷结构】

每卷结构：
- 开局（1-2章）：建立新环境/新危机
- 发展（3-N-2章）：层层递进
- 高潮（N-1章）：大冲突爆发
- 结尾（N章）：悬念收尾，新伏笔

请严格按照以上结构设计原则进行大纲规划。"""
    
    def design_novel_structure(
        self,
        context: OutlineContext
    ) -> Dict[str, Any]:
        """设计小说整体结构"""
        if not self.llm:
            return self._fallback_structure(context)
        
        prompt = f"""请为小说《{context.novel_title}》设计整体结构：

- 题材：{context.genre}
- 风格：{context.tone}
- 目标字数：{context.target_word_count}字
- 章节数：{context.chapter_count}章

请设计：
1. 卷结构（分几卷，每卷主题）
2. 主线剧情
3. 情感线
4. 核心冲突
5. 升级体系
"""
        
        response = self.llm.generate(
            system_prompt=self.get_system_prompt(),
            user_prompt=prompt,
            max_tokens=2000,
            temperature=0.7
        )
        
        return self._parse_structure_response(response, context)
    
    def design_volume_outline(
        self,
        volume_num: int,
        volume_title: str,
        chapter_count: int,
        genre: str
    ) -> List[Dict[str, str]]:
        """设计单卷章节大纲"""
        if not self.llm:
            return self._fallback_chapter_outlines(volume_num, chapter_count)
        
        prompt = f"""请为第{volume_num}卷「{volume_title}」设计{chapter_count}章的大纲：

题材：{genre}

每章大纲需包含：
- 章节核心事件
- 主要冲突
- 爽点设计
- 悬念钩子

请按以下格式输出：
第1章：标题 | 核心事件 | 冲突 | 爽点 | 悬念
第2章：...
"""
        
        response = self.llm.generate(
            system_prompt=self.get_system_prompt(),
            user_prompt=prompt,
            max_tokens=1500,
            temperature=0.7
        )
        
        return self._parse_chapter_outlines(response, volume_num)
    
    def design_chapter_outline(
        self,
        chapter_num: int,
        volume_num: int,
        previous_outline: str,
        genre: str
    ) -> str:
        """设计单章详细大纲"""
        if not self.llm:
            return self._fallback_chapter_outline(chapter_num)
        
        prompt = f"""请设计第{volume_num}卷第{chapter_num}章的详细大纲：

题材：{genre}

前章大纲：
{previous_outline}

请设计：
1. 章节标题
2. 核心事件（200字）
3. 情节发展（详细）
4. 情感转折
5. 悬念/伏笔
6. 爽点设计
7. 章尾钩子
"""
        
        response = self.llm.generate(
            system_prompt=self.get_system_prompt(),
            user_prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response
    
    def _fallback_structure(self, context: OutlineContext) -> Dict[str, Any]:
        """备用结构设计"""
        volume_count = max(1, context.chapter_count // 30)
        chapters_per_volume = context.chapter_count // volume_count
        
        volumes = []
        for i in range(volume_count):
            volumes.append({
                "volume_num": i + 1,
                "volume_title": f"第{i+1}卷",
                "chapter_range": f"第{i*chapters_per_volume+1}章-第{(i+1)*chapters_per_volume}章",
                "theme": "发展" if i > 0 else "开局",
                "arc_goal": "建立世界观" if i == 0 else "推进主线"
            })
        
        return {
            "volume_count": volume_count,
            "chapters_per_volume": chapters_per_volume,
            "volumes": volumes,
            "total_chapters": context.chapter_count,
            "estimated_word_count": context.target_word_count
        }
    
    def _fallback_chapter_outlines(
        self,
        volume_num: int,
        chapter_count: int
    ) -> List[Dict[str, str]]:
        """备用章节大纲"""
        outlines = []
        
        for i in range(chapter_count):
            chapter_num = i + 1
            
            if chapter_num == 1:
                event = "开局冲突建立，主角出场"
                conflict = "主角困境"
                shuangdian = "金手指初现"
                hook = "悬念留白"
            elif chapter_num == 2:
                event = "金手指展示"
                conflict = "能力受限"
                shuangdian = "小试牛刀"
                hook = "更大的危机"
            elif chapter_num == 3:
                event = "第一次高潮"
                conflict = "强敌出现"
                shuangdian = "越级战胜"
                hook = "身份暴露危机"
            else:
                event = "情节推进"
                conflict = "新障碍"
                shuangdian = "稳扎稳打"
                hook = "下一章预告"
            
            outlines.append({
                "chapter_num": chapter_num,
                "title": f"第{chapter_num}章",
                "core_event": event,
                "conflict": conflict,
                "shuangdian": shuangdian,
                "hook": hook
            })
        
        return outlines
    
    def _fallback_chapter_outline(self, chapter_num: int) -> str:
        """备用单章大纲"""
        return f"""第{chapter_num}章大纲

核心事件：情节推进
情节发展：
- 开局冲突
- 中段发展
- 结尾高潮

情感转折：角色成长
悬念/伏笔：待回收
爽点设计：根据题材
章尾钩子：引发好奇
"""
    
    def _parse_structure_response(
        self,
        response: str,
        context: OutlineContext
    ) -> Dict[str, Any]:
        """解析结构响应"""
        return {
            "response": response,
            "volume_count": max(1, context.chapter_count // 30),
            "chapters_per_volume": context.chapter_count // max(1, context.chapter_count // 30)
        }
    
    def _parse_chapter_outlines(
        self,
        response: str,
        volume_num: int
    ) -> List[Dict[str, str]]:
        """解析章节大纲响应"""
        outlines = []
        lines = response.strip().split('\n')
        
        for line in lines:
            if '：' in line or ':' in line:
                outlines.append({
                    "chapter_num": len(outlines) + 1,
                    "raw": line
                })
        
        if not outlines:
            return self._fallback_chapter_outlines(volume_num, 10)
        
        return outlines
