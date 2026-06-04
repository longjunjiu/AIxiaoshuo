# AIxiaoshuo — AI小说辅助创作系统

<p align="center">
  <img src="https://img.shields.io/github/stars/longjunjiu/AIxiaoshuo" alt="stars">
  <img src="https://img.shields.io/github/forks/longjunjiu/AIxiaoshuo" alt="forks">
  <img src="https://img.shields.io/github/license/longjunjiu/AIxiaoshuo" alt="license">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="python">
</p>

<p align="center">
  <strong>百万字级长篇网络小说 AI 辅助创作系统<br>多 Agent 协作 · 三层记忆 · LLM 深度审计 · 多层去 AI 味</strong>
</p>

---

## 为什么选择 AIxiaoshuo？

| 传统写作痛点 | AIxiaoshuo 解法 |
|:---|:---|
| 灵感枯竭，卡文严重 | 6 类冲突 × 90 个情节方案库 |
| 前后矛盾，设定打架 | 三层记忆系统，全书一致性保障 |
| AI 味太重，读者出戏 | 多层 AIGC 检测 + LLM 语义级润色 |
| 质量参差不齐 | 26 维度质量审计 + 多视角评审团 |
| 单模型生成，效果单一 | 5 Agent 协作，媲美专业编辑流程 |

---

## 核心架构

### 多 Agent 协作流程

```
┌────────────────────────────────────────────────────────────┐
│                   Orchestrator (编排器)                     │
│                                                             │
│  [1] Architect  →  [2] Writer  →  [3] Auditor              │
│  (建筑师规划)       (写手生成)       (审计员检查)            │
│                                         ↓                   │
│                    [5] Panel   ←  [4] Reviser               │
│                    (评审团投票)     (修订者优化)              │
│                         ↓                                   │
│               通过? → 保存  |  不通过? → 重新迭代            │
└────────────────────────────────────────────────────────────┘
```

| Agent | 核心职责 | LLM 可用时 | 无 LLM 时 |
|:---|:---|:---|:---|
| **Architect** | 规划章节结构、设计伏笔 | JSON 结构化大纲 | 内置模板大纲 |
| **Writer** | 生成高质量正文 | LLM 全文生成 | 返回配置提示 |
| **Auditor** | 26 维度质量审计 | LLM 深度评审 | 静态规则检测 |
| **Reviser** | 文风优化、去 AI 味 | LLM 语义润色 | 规则替换 |
| **Panel** | 5 视角多角色投票 | 独立评审 + 加权得分 | 默认 7.0 通过 |

### 三层记忆系统

```
┌────────────────────────────────────────────────┐
│  Long-term Memory（全书级）                     │
│  · 世界观设定  · 角色状态  · 伏笔网络          │
│  · 真相文件    · 资源账本                      │
├────────────────────────────────────────────────┤
│  Mid-term Memory（卷级）                        │
│  · 章节摘要    · 支线追踪  · 情感弧线          │
├────────────────────────────────────────────────┤
│  Short-term Memory（章节级）                   │
│  · 当前大纲    · 写作上下文  · 草稿迭代        │
└────────────────────────────────────────────────┘
```

**记忆与写作深度整合**：写手生成每章前，系统自动拉取三层记忆上下文（待回收伏笔、角色当前状态、前文摘要），注入提示词，保障叙事连贯性。

### 26 维度质量审计

| 类别 | 审计项（示例）|
|:---|:---|
| 剧情逻辑 | 情节自洽、因果关系、伏笔呼应、时间线一致 |
| 人物塑造 | 性格一致、行为自洽、对话自然、信息边界 |
| 文风质量 | 句式变化、节奏把控、AI 词汇密度 |
| 世界观 | 设定统一、体系自洽、细节一致 |
| 爽点设计 | 爽点密度、高潮节奏、钩子设计 |

### AIGC 检测与去 AI 味

| 层级 | 检测内容 | 处理方式 |
|:---|:---|:---|
| **Tier 1** | 致命 AI 词汇（delve、利用等） | 强制替换 |
| **Tier 2** | 可疑词汇聚类（连续 3+ 个） | 标记预警 |
| **Tier 3** | 无信息填充语句 | 建议删除 |
| **结构层** | 段落/句子长度均匀性 | 统计风险分 |
| **语义层** | LLM 语义级润色 | 整体改写 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/longjunjiu/AIxiaoshuo.git
cd AIxiaoshuo/NovelForge

# 安装核心依赖
pip install -r requirements.txt

# 如需使用 OpenAI / DeepSeek 等
pip install openai

# 如需使用 Anthropic Claude
pip install anthropic
```

### 配置 LLM

**NVIDIA NIM（免费，推荐新手）**
```bash
export LLM_PROVIDER=nvidia
export API_KEY="nvapi-xxxxxx"
```

**OpenAI**
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY="sk-xxxxxx"
```

**Anthropic Claude**
```bash
export LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY="sk-ant-xxxxxx"
```

**DeepSeek（国内高性价比）**
```bash
export LLM_PROVIDER=deepseek
export API_KEY="sk-xxxxxx"
```

**本地 Ollama**
```bash
export LLM_PROVIDER=ollama
# 无需 API Key
```

### 创建小说项目

```bash
# 1. 创建项目
python main.py create \
  --title "逆天改命" \
  --genre xuanhuan \
  --synopsis "平凡少年在废墟中获得上古传承，踏上逆天修仙复仇之路" \
  --chapters 1000 --words 3000

# 2. 生成世界观和角色设定
python main.py settings \
  --project ./novels/逆天改命 \
  --themes "复仇,成长,热血"

# 3. 生成全书大纲
python main.py outline \
  --project ./novels/逆天改命 \
  --volumes 10 --chapters-per-volume 100

# 4. 写作（单章）
python main.py write \
  --project ./novels/逆天改命 \
  --chapter 1 \
  --guidance "本章重点：主角初次展示金手指，反派被打脸"

# 5. 批量写作
python main.py batch \
  --project ./novels/逆天改命 \
  --start 1 --end 50 --checkpoint 10

# 6. 查看状态
python main.py status --project ./novels/逆天改命

# 7. 导出
python main.py export --project ./novels/逆天改命 --format markdown
```

### CLI 完整命令参考

```bash
python main.py [全局选项] <命令> [命令选项]

全局选项：
  -P  --provider     LLM 提供商 (openai/anthropic/deepseek/nvidia/ollama/...)
  -K  --api-key      API 密钥
  -U  --base-url     API 基础 URL
  -M  --model        模型名称
  -T  --temperature  温度 (默认 0.7)

命令：
  create    创建新书项目
  settings  生成世界观/角色设定
  outline   生成全书大纲
  write     写作单章（含审计、修订）
  batch     批量写作
  audit     审计指定章节
  detect    AIGC 检测
  hooks     查看伏笔追踪状态
  status    查看项目状态
  export    导出书稿 (markdown/text/json)
```

---

## Python API 使用

```python
from skills.novel_forge import NovelForge, ForgeConfig

# 配置
config = ForgeConfig(
    llm_provider="deepseek",
    api_key="sk-xxxxxx",
    model="deepseek-chat",
    temperature=0.7,
    max_tokens=4096,
    top_p=0.9,
)

forge = NovelForge(config)

# 创建项目
project = forge.create_project(
    title="逆天改命",
    genre="xuanhuan",
    synopsis="少年修仙复仇之路",
    target_chapters=1000,
    target_words_per_chapter=3000,
)

# 生成设定（LLM 生成世界观、角色、体系）
settings = forge.generate_settings(themes=["复仇", "成长", "热血"])

# 生成大纲
outline_path = forge.generate_outline(num_volumes=10, chapters_per_volume=100)

# 写作（多 Agent 协作，含记忆注入、审计、修订、评审）
result = forge.write_chapter(chapter_num=1, auto_audit=True, auto_revise=True)
print(f"字数: {result['word_count']}, 通过: {result['success']}")

# 单独审计（LLM 深度评审）
audit = forge.audit_chapter(chapter_num=1)
print(f"评分: {audit['score']:.1f}, AI特征: {audit['ai_tells']['severity']}")

# 单独修订（支持 polish/rewrite/rework/anti-detect 四种模式）
revision = forge.revise_chapter(chapter_num=1, mode="polish")

# AIGC 检测
detect = forge.detect_aigc(chapter_num=1)
print(f"风险: {detect['risk_level']}, Tier1词汇: {detect['tier1_count']}")

# 伏笔追踪
hooks = forge.track_hooks()
print(f"待回收: {hooks['pending_count']}, 已回收: {hooks['recycled_count']}")

# 项目状态
status = forge.get_status()

# 导出书稿
forge.export_book(format="markdown")
```

---

## 高级配置

### YAML 配置文件

```yaml
# config.yaml
llm_provider: deepseek
api_key: "sk-xxxxxx"
model: "deepseek-chat"
temperature: 0.75
max_tokens: 4096
top_p: 0.9
frequency_penalty: 0.1
presence_penalty: 0.0
```

使用时：
```bash
python main.py --config config.yaml write --project ./novels/逆天改命 --chapter 1
```

### 支持的 LLM 提供商

| 提供商 | 环境变量 / API Key | 默认模型 |
|:---|:---|:---|
| `openai` | `OPENAI_API_KEY` | gpt-4 |
| `anthropic` | `ANTHROPIC_API_KEY` | claude-3-opus-20240229 |
| `deepseek` | `API_KEY` | deepseek-chat |
| `nvidia` | `API_KEY` | meta/llama-3.1-70b-instruct |
| `qwen` | `API_KEY` | qwen-plus |
| `zhipu` | `API_KEY` | glm-4 |
| `ollama` | 无需 | llama3 |
| `custom` | `API_KEY` | gpt-4 |

---

## 项目结构

```
NovelForge/
├── requirements.txt              # 依赖清单
├── main.py                       # CLI 主入口
├── generate_content.py           # 交互式生成脚本
├── gen_batch.py                  # 批量生成脚本
├── gen_chapter.py                # 单章生成脚本
│
├── skills/novel_forge/           # 核心模块
│   ├── __init__.py               # NovelForge 主类 + ForgeConfig
│   ├── novel_manager.py          # 项目创建/加载/导出
│   │
│   ├── agents/                   # 多 Agent 系统
│   │   ├── orchestrator.py       # 编排器（协调所有 Agent）
│   │   ├── architect.py          # 建筑师（章节大纲规划）
│   │   ├── writer.py             # 写手（正文生成）
│   │   ├── auditor.py            # 审计员（质量检查）
│   │   ├── reviser.py            # 修订者（文风优化）
│   │   └── panel.py              # 评审团（多视角投票）
│   │
│   ├── memory/                   # 三层记忆系统
│   │   ├── long_term.py          # 长期记忆（伏笔/事实/角色状态）
│   │   ├── mid_term.py           # 中期记忆（卷摘要/支线/情感弧线）
│   │   └── short_term.py         # 短期记忆（章节大纲/上下文）
│   │
│   ├── rules/                    # 创作规则引擎
│   │   ├── anti_slop.py          # 多层 AIGC 检测规则
│   │   ├── classic_novels.py     # 十大经典网文写作范式
│   │   ├── craft.py              # 通用写作技法
│   │   └── genre_rules.py        # 题材专属规则
│   │
│   ├── audit/
│   │   └── detector.py           # AIGC 检测器
│   │
│   └── utils/
│       ├── llm_client.py         # 多提供商 LLM 客户端（含重试）
│       └── file_ops.py           # 文件操作工具
│
└── novels/                       # 生成的小说项目目录
    └── <书名>/
        ├── config.yaml
        ├── outline.md
        ├── settings/             # 世界观/角色/体系设定
        ├── volumes/              # 按卷存储章节
        │   └── volume_1/
        │       ├── outline.md
        │       ├── chapters/     # ch_001.md, ch_002.md ...
        │       └── memory/       # 卷级记忆文件
        ├── memory/               # 全书记忆文件
        │   ├── canon.md          # 真相文件
        │   ├── hook_network.md   # 伏笔网络
        │   └── resource_ledger.md
        └── exports/              # 导出书稿
```

---

## 十大经典网文写作范式

内置对以下作品写作技法的深度分析，用于指导 AI 生成：

| 作品 | 核心技法 |
|:---|:---|
| 《斗破苍穹》 | 退婚流开山，爽点密集，三年之约节奏 |
| 《凡人修仙传》 | 猥琐发育，资源积累，越阶流 |
| 《斗罗大陆》 | 体系创新，双主角，全员成长 |
| 《遮天》 | 宏大世界观，群像战斗，悲剧与热血 |
| 《完美世界》 | 子时代史诗，战斗描写，情感厚重 |
| 《仙逆》 | 顺则凡逆则仙，孤独成仙路 |
| 《全职高手》 | 网游竞技巅峰，职业化描写 |
| 《诡秘之主》 | 信息差悬念，氛围营造，异世界构建 |
| 《牧神记》 | 东方玄幻创新，哲学融入 |
| 《雪中悍刀行》 | 人物群像，文笔优美，武侠精神 |

---

## 许可证

MIT License

---

**AIxiaoshuo** — 让 AI 成为你的最佳写作搭档
