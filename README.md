# AIxiaoshuo - AI小说辅助创作系统

## 项目简介

**AIxiaoshuo** 是一个专为辅助创作百万字级别长篇网络小说而设计的AI技能系统。支持多Agent协作、多模型调用、交互式创作，专为网文作家打造。

## 核心功能

### 🤖 多Agent协作系统
- **建筑师Agent**：规划章节结构、埋设伏笔
- **写手Agent**：生成高质量正文内容  
- **审计Agent**：26维度质量检查
- **修订Agent**：优化文风、去AI味
- **评审团Agent**：多视角评审把关

### 📚 三层记忆系统
- **短期记忆**：当前章节上下文
- **中期记忆**：当前卷剧情连贯
- **长期记忆**：全书设定统一

### 🎯 90个情节方案库
6种冲突类型 × 5个章节阶段 × 3个情节方案：
- 退婚流、灭门流、废物流、穿越流、争锋流、逆袭流

### 🔧 多模型支持
| 提供商 | 说明 |
|--------|------|
| NVIDIA NIM | 免费Llama-3.1-70B |
| OpenAI | GPT-4/3.5 |
| Anthropic | Claude-3 |
| DeepSeek | 国产高性能 |
| Ollama | 本地模型 |

### 📖 十大经典网文学习
内置经典网文写作指南，参考《斗破苍穹》《凡人修仙传》等作品风格。

## 快速开始

```bash
# 进入项目目录
cd NovelForge

# 安装依赖
pip install pyyaml requests

# 使用NVIDIA免费API生成小说
export NVIDIA_API_KEY="your-key"
python gen_batch.py
```

## 项目结构

```
AIxiaoshuo/
├── NovelForge/           # 项目主目录
│   ├── skills/novel_forge/    # 核心技能
│   ├── novels/               # 生成的小说
│   ├── generate_content.py   # 交互式生成器
│   └── gen_batch.py          # 批量生成脚本
├── taigu_shenwang.epub   # 参考小说
└── README.md             # 本文件
```

## 适用场景

- ✅ 百万字长篇网络小说
- ✅ 多卷系列作品  
- ✅ 玄幻/仙侠/都市多题材
- ✅ 批量章节生成

## 许可证

MIT License
