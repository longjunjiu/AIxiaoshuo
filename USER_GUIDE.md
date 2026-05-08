# NovelForge 使用指南

## 快速开始

### 1. 安装

```bash
# 克隆项目
git clone <repository-url>
cd NovelForge

# 安装依赖
pip install pyyaml requests

# 配置API密钥
export OPENAI_API_KEY="your-api-key"
# 或
export ANTHROPIC_API_KEY="your-api-key"
```

### 2. 创建新书

```bash
python main.py create \
  --title "我的玄幻小说" \
  --genre xuanhuan \
  --synopsis "一个少年成长为强者的故事" \
  --chapters 1000 \
  --words 3000
```

### 3. 生成设定

```bash
python main.py settings --project ./novels/我的玄幻小说 --themes "成长,复仇,热血"
```

### 4. 生成大纲

```bash
python main.py outline --project ./novels/我的玄幻小说 --volumes 10
```

### 5. 写作章节

```bash
# 单章写作
python main.py write --project ./novels/我的玄幻小说 --chapter 1

# 带指导写作
python main.py write --project ./novels/我的玄幻小说 --chapter 2 \
  --guidance "本章重点写主角获得奇遇"
```

### 6. 批量写作

```bash
python main.py batch --project ./novels/我的玄幻小说 \
  --start 1 --end 10 --checkpoint 5
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `create` | 创建新书 |
| `settings` | 生成设定 |
| `outline` | 生成大纲 |
| `write` | 写作单章 |
| `batch` | 批量写作 |
| `audit` | 审计章节 |
| `detect` | AIGC检测 |
| `hooks` | 伏笔追踪 |
| `status` | 查看状态 |
| `export` | 导出书籍 |

## 配置说明

### 环境变量

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# 或 Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
export LLM_PROVIDER="anthropic"

# 模型选择
export LLM_MODEL="gpt-4"  # 或 claude-3-opus
```

### 配置文件

创建 `config.yaml`:

```yaml
llm_provider: openai
api_key: "your-api-key"
base_url: "https://api.openai.com/v1"
model: "gpt-4"
temperature: 0.7
max_tokens: 4096
```

## 题材说明

| 题材ID | 说明 |
|--------|------|
| `xuanhuan` | 玄幻 |
| `xianxia` | 仙侠 |
| `urban` | 都市 |
| `scifi` | 科幻 |
| `horror` | 恐怖 |
| `general` | 通用 |

## 项目结构

```
novels/我的玄幻小说/
├── config.yaml              # 配置文件
├── settings/               # 设定目录
│   ├── world.md           # 世界观
│   ├── characters.md      # 角色
│   ├── system.md          # 体系
│   └── magic.md           # 特殊设定
├── volumes/               # 卷目录
│   ├── volume_1/
│   │   ├── outline.md    # 卷大纲
│   │   ├── chapters/     # 章节
│   │   └── memory/       # 卷记忆
│   └── volume_N/
├── memory/                # 全书记忆
│   ├── canon.md          # 真相文件
│   ├── hook_network.md   # 伏笔网络
│   └── resource_ledger.md # 资源账本
└── exports/               # 导出文件
```

## 创作规则

### 去AI味规则

1. **禁用词汇**: delve, utilize, leverage 等
2. **避免句式**: "不只是X，而是Y"
3. **段落变化**: 长度要有起伏
4. **句长变化**: 模仿人类写作节奏
5. **对话自然**: 角色有独特说话风格

### 伏笔管理

系统自动追踪伏笔：
- 植入时记录
- 到期前提醒
- 回收后标记

### 审计维度

26个审计维度，自动应用于对应题材。

## API调用示例

```python
from novel_forge import NovelForge, ForgeConfig

config = ForgeConfig(
    llm_provider="openai",
    api_key="your-key",
    model="gpt-4"
)

forge = NovelForge(config)

# 创建项目
project = forge.create_project(
    title="我的小说",
    genre="xuanhuan",
    synopsis="...",
    target_chapters=500
)

# 加载项目
forge.load_project("./novels/我的小说")

# 生成设定
forge.generate_settings(themes=["成长", "热血"])

# 生成大纲
forge.generate_outline(num_volumes=5)

# 写作
result = forge.write_chapter(chapter_num=1)

# 审计
audit = forge.audit_chapter(chapter_num=1)

# AIGC检测
detect = forge.detect_aigc(chapter_num=1)

# 导出
forge.export_book(format="markdown")
```
