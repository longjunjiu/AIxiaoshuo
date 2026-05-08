# NovelForge - AI小说辅助创作技能

## 项目概述

**NovelForge** 是一个专为辅助创作百万字级别长篇网络小说而设计的AI技能系统。它结合了多个开源项目的最佳实践，并加入了独创功能来解决长篇小说创作中的核心难题。

### 核心特性

| 特性 | 描述 |
|------|------|
| 🧠 多层记忆系统 | 短期/中期/长期三层记忆架构，确保百万字级别的上下文连贯 |
| 🎭 6大Agent协作 | 建筑师、写手、审计员、修订者、评审团、编排器 |
| 📊 26维度审计 | 从剧情逻辑到文风一致性的全方位质量把控 |
| 🎯 智能伏笔网络 | 自动追踪、提醒、回收伏笔，确保埋线不遗漏 |
| 🛡️ AIGC检测与去AI味 | 多层检测机制 + 反检测改写，让AI文不再被识别 |
| 📚 分卷管理体系 | 百万字分卷管理，每卷独立闭环又与全书联动 |
| 🔄 自适应优化 | 读者反馈驱动创作方向动态调整 |
| 🎨 多题材支持 | 玄幻、仙侠、都市、科幻、恐怖、通用六大题材 |
| 🔧 多模型支持 | OpenAI/Anthropic/Ollama/HuggingFace/Qwen/Zhipu/DeepSeek |

### 支持的LLM提供商

| 提供商 | 类型 | 默认模型 | 基础URL |
|--------|------|----------|----------|
| OpenAI | 云端API | gpt-4 | https://api.openai.com/v1 |
| Anthropic | 云端API | claude-3-opus | https://api.anthropic.com/v1 |
| Ollama | 本地 | llama3 | http://localhost:11434/v1 |
| HuggingFace | 本地 | Llama-2-7b | - |
| DeepSeek | 云端API | deepseek-chat | https://api.deepseek.com/v1 |
| Qwen | 云端API | qwen-plus | https://api.qwenlm.com/v1 |
| Zhipu | 云端API | glm-4 | https://open.bigmodel.cn/api/paas/v4 |
| API2D | 代理API | gpt-4 | https://api2d.com/v1 |
| Custom | 自定义 | - | 用户指定 |

### 技术架构

```
NovelForge/
├── skills/novel_forge/           # 技能主目录
│   ├── agents/                   # Agent实现
│   │   ├── architect.py         # 建筑师：规划章节结构
│   │   ├── writer.py           # 写手：生成正文
│   │   ├── auditor.py          # 审计员：质量检查
│   │   ├── reviser.py          # 修订者：修改优化
│   │   ├── panel.py            # 评审团：多视角评审
│   │   └── orchestrator.py     # 编排器：流程控制
│   ├── memory/                   # 记忆系统
│   │   ├── short_term.py       # 短期记忆（当前章）
│   │   ├── mid_term.py         # 中期记忆（当前卷）
│   │   └── long_term.py        # 长期记忆（全书）
│   ├── audit/                   # 审计系统
│   │   ├── continuity.py       # 连续性检查
│   │   ├── foreshadow.py       # 伏笔检查
│   │   ├── pacing.py           # 节奏检查
│   │   ├── voice.py            # 文风检查
│   │   └── detect.py           # AIGC检测
│   ├── rules/                   # 创作规则
│   │   ├── craft.py            # 通用创作规则
│   │   ├── anti_slop.py        # 反AI味规则
│   │   ├── genres/             # 题材规则
│   │   │   ├── xuanhuan.py     # 玄幻规则
│   │   │   ├── xianxia.py      # 仙侠规则
│   │   │   ├── urban.py        # 都市规则
│   │   │   ├── sci_fi.py      # 科幻规则
│   │   │   └── horror.py       # 恐怖规则
│   │   └── book_rules.py       # 单本书规则
│   ├── utils/                   # 工具函数
│   │   ├── vector_store.py     # 向量存储
│   │   ├── llm_client.py       # LLM客户端
│   │   └── file_ops.py         # 文件操作
│   ├── prompts/                 # 提示词模板
│   │   ├── architect_prompt.py
│   │   ├── writer_prompt.py
│   │   ├── auditor_prompt.py
│   │   └── ...
│   ├── novel_manager.py         # 小说管理器
│   └── main.py                  # 入口文件
└── SPEC.md                       # 技能规格说明
```

### 工作流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                        NovelForge 创作管线                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │
│  │  建筑师  │───▶│  写手   │───▶│  审计员  │───▶│  修订者  │         │
│  │Architect│    │ Writer  │    │ Auditor │    │ Reviser │         │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘         │
│       │               │               │               │             │
│       ▼               ▼               ▼               ▼             │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │                      记忆系统                            │       │
│  │  短期记忆 ──▶ 中期记忆 ──▶ 长期记忆                      │       │
│  │  (当前章)      (当前卷)      (全书)                       │       │
│  └─────────────────────────────────────────────────────────┘       │
│                              │                                      │
│                              ▼                                      │
│                     ┌─────────────┐                               │
│                     │   评审团     │                               │
│                     │   Panel      │                               │
│                     └─────────────┘                               │
│                              │                                      │
│                              ▼                                      │
│                     ┌─────────────┐                               │
│                     │   编排器     │                               │
│                     │Orchestrator │                               │
│                     └─────────────┘                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 安装与使用

```bash
# 安装依赖
pip install pyyaml requests numpy tiktoken

# 可选：安装本地模型支持
pip install transformers accelerate bitsandbytes
```

### 配置说明

#### 使用环境变量

```bash
# OpenAI
export OPENAI_API_KEY="your-api-key"

# Anthropic
export ANTHROPIC_API_KEY="your-api-key"
export LLM_PROVIDER="anthropic"

# Ollama（本地）
export LLM_PROVIDER="ollama"
export LLM_MODEL="llama3"

# 自定义模型
export LLM_PROVIDER="custom"
export LLM_MODEL="your-model"
export LLM_BASE_URL="http://localhost:8000/v1"
```

#### 使用配置文件

创建 `config.yaml`:

```yaml
llm_provider: ollama
model: llama3
base_url: http://localhost:11434/v1
temperature: 0.7
max_tokens: 4096
```

#### CLI命令

```bash
# 创建新书
python main.py create --title "我的小说" --genre xuanhuan

# 指定模型提供商
python main.py write --project ./novels/我的小说 --chapter 1 \
  --provider ollama --model llama3

# 使用自定义API
python main.py write --project ./novels/我的小说 --chapter 1 \
  --provider custom --base-url http://localhost:8000/v1 \
  --model my-model --api-key my-key
```

### 本地模型使用

#### Ollama

```bash
# 安装Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 下载模型
ollama pull llama3

# 运行服务（默认端口11434）
ollama serve

# 使用
python main.py write --project ./novels/my_novel --chapter 1 \
  --provider ollama --model llama3
```

#### HuggingFace

```bash
# 使用本地HuggingFace模型
python main.py write --project ./novels/my_novel --chapter 1 \
  --provider huggingface --model meta-llama/Llama-2-7b-chat-hf
```

### 适用场景

- ✅ 百万字级别网络小说创作
- ✅ 多卷长篇系列作品
- ✅ 需要严格世界观的奇幻/科幻小说
- ✅ 追求剧情连贯性的悬疑/推理小说
- ✅ 批量生成高质量章节草稿

### 许可证

MIT License
