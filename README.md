# AIxiaoshuo - AI小说辅助创作系统

![GitHub stars](https://img.shields.io/github/stars/longjunjiu/AIxiaoshuo)
![GitHub forks](https://img.shields.io/github/forks/longjunjiu/AIxiaoshuo)
![License](https://img.shields.io/github/license/longjunjiu/AIxiaoshuo)

## 🌟 项目简介

**AIxiaoshuo** 是一个专为辅助创作百万字级别长篇网络小说而设计的AI技能系统。通过多Agent协作、三层记忆系统和交互式创作流程，为网文作家提供专业的写作辅助工具。

## 🎯 核心功能

### 🤖 多Agent协作系统
| Agent | 职责 |
|-------|------|
| **建筑师** | 规划章节结构、埋设伏笔 |
| **写手** | 生成高质量正文内容 |
| **审计员** | 26维度质量检查 |
| **修订者** | 优化文风、去AI味 |
| **评审团** | 多视角评审把关 |

### 📚 三层记忆系统
- **短期记忆**：当前章节上下文管理
- **中期记忆**：当前卷剧情连贯性维护
- **长期记忆**：全书设定统一性保障

### 🎲 90个情节方案库
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
| HuggingFace | 开源模型 |
| 自定义API | 灵活扩展 |

### 📖 经典网文学习
内置十大经典网文写作指南，深度参考：
- 《斗破苍穹》《凡人修仙传》《斗罗大陆》
- 《遮天》《完美世界》《仙逆》
- 《全职高手》《诡秘之主》《牧神记》《雪中悍刀行》

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/longjunjiu/AIxiaoshuo.git
cd AIxiaoshuo/NovelForge

# 安装依赖
pip install pyyaml requests

# 使用NVIDIA免费API生成小说
export NVIDIA_API_KEY="your-key"
python gen_batch.py
```

## 📁 项目结构

```
AIxiaoshuo/
├── NovelForge/              # 主项目目录
│   ├── skills/novel_forge/  # 核心技能模块
│   │   ├── agents/          # Agent实现
│   │   ├── memory/          # 记忆系统
│   │   ├── rules/           # 创作规则
│   │   └── utils/           # 工具函数
│   ├── novels/              # 生成的小说
│   ├── generate_content.py  # 交互式生成器
│   ├── gen_batch.py         # 批量生成脚本
│   ├── gen_chapter.py       # 单章生成脚本
│   └── main.py              # 主入口
├── taigu_shenwang.epub      # 参考小说示例
└── README.md                # 项目简介
```

## 🎮 使用方式

### 1. 交互式创作（推荐）
```bash
python generate_content.py
```

### 2. 批量生成章节
```bash
python gen_batch.py --start 1 --end 100
```

### 3. 单章生成
```bash
python gen_chapter.py --chapter 1
```

## ✨ 特色亮点

- ✅ **百万字级支持**：专为长篇小说设计
- ✅ **交互式决策**：每个步骤提供多方案选择
- ✅ **去AI味处理**：多层AIGC检测与文风优化
- ✅ **质量审计**：26维度全方位把控
- ✅ **本地部署**：支持Ollama等本地模型

## 📝 测试成果

已成功生成测试小说《星辰剑影》100章，约10万字内容。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**AIxiaoshuo** - 让AI成为你的最佳写作搭档