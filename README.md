# AIxiaoshuo — AI小说辅助创作系统

<p align="center">
  <img src="https://img.shields.io/github/stars/longjunjiu/AIxiaoshuo" alt="stars">
  <img src="https://img.shields.io/github/forks/longjunjiu/AIxiaoshuo" alt="forks">
  <img src="https://img.shields.io/github/license/longjunjiu/AIxiaoshuo" alt="license">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="python">
</p>

<p align="center">
  <strong>百万字级长篇网络小说 AI 辅助创作系统</strong><br>
  多 Agent 协作 · 三层记忆 · LLM 深度审计 · 多层去 AI 味
</p>

---

## 简介

**AIxiaoshuo** 是一套专为长篇网络小说辅助创作设计的 AI 系统。核心子项目 **NovelForge** 通过 5 个专职 Agent 的协作流程，将"规划—生成—审计—修订—评审"完整闭环，并以三层记忆系统（Long-term / Mid-term / Short-term）保障百万字级作品的前后一致性。

---

## 核心特性

| 特性 | 说明 |
|:---|:---|
| **5 Agent 协作** | 建筑师规划 → 写手生成 → 审计员检查 → 修订者润色 → 评审团投票 |
| **三层记忆系统** | 全书伏笔/事实追踪，跨章节角色状态同步，前文摘要自动注入 |
| **LLM 深度审计** | 26 维度质量检查，JSON 结构化评分，静态规则兜底 |
| **智能修订** | 支持 polish/rewrite/rework 四种模式，语义级去 AI 味 |
| **多提供商支持** | OpenAI、Anthropic、DeepSeek、NVIDIA、Qwen、Ollama 等 |
| **伏笔追踪** | 植入/回收/逾期三态管理，自动提醒即将到期伏笔 |
| **AIGC 检测** | 三层词汇检测 + 结构均匀性分析 + 段落模式识别 |

---

## 快速开始

```bash
git clone https://github.com/longjunjiu/AIxiaoshuo.git
cd AIxiaoshuo/NovelForge

pip install -r requirements.txt
pip install openai          # 或 anthropic / 其他 SDK

export OPENAI_API_KEY="sk-xxxxxx"   # 或其他提供商的 Key

# 创建项目
python main.py create --title "逆天改命" --genre xuanhuan \
  --synopsis "平凡少年获得上古传承，踏上逆天修仙之路"

# 生成设定 + 大纲
python main.py settings --project ./novels/逆天改命
python main.py outline  --project ./novels/逆天改命 --volumes 10

# 写作（多 Agent 协作）
python main.py write --project ./novels/逆天改命 --chapter 1

# 批量写作
python main.py batch --project ./novels/逆天改命 --start 1 --end 100
```

详细文档请参阅 [NovelForge/README.md](NovelForge/README.md)。

---

## 项目结构

```
AIxiaoshuo/
├── NovelForge/              # 主项目
│   ├── requirements.txt     # 依赖清单
│   ├── main.py              # CLI 入口
│   ├── skills/novel_forge/  # 核心模块
│   │   ├── agents/          # 5 Agent 实现
│   │   ├── memory/          # 三层记忆系统
│   │   ├── rules/           # 创作规则引擎
│   │   ├── audit/           # AIGC 检测
│   │   └── utils/           # LLM 客户端
│   ├── novels/              # 生成的小说项目
│   └── README.md            # 详细文档
└── README.md
```

---

## 许可证

MIT License
