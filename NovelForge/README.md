# NovelForge - AI小说创作核心模块

本目录包含AIxiaoshuo项目的核心代码实现。

## 📁 目录结构

```
NovelForge/
├── skills/novel_forge/     # 核心技能模块
│   ├── agents/             # 多Agent系统
│   │   ├── architect.py    # 建筑师Agent
│   │   ├── writer.py       # 写手Agent
│   │   ├── auditor.py      # 审计Agent
│   │   ├── reviser.py      # 修订Agent
│   │   ├── panel.py        # 评审团Agent
│   │   └── orchestrator.py # 编排器
│   ├── memory/             # 三层记忆系统
│   │   ├── short_term.py   # 短期记忆
│   │   ├── mid_term.py     # 中期记忆
│   │   └── long_term.py    # 长期记忆
│   ├── rules/              # 创作规则
│   │   ├── classic_novels.py # 经典网文学习
│   │   ├── anti_slop.py    # 去AI味规则
│   │   ├── craft.py        # 写作技巧
│   │   └── genre_rules.py  # 题材规则
│   ├── utils/              # 工具函数
│   │   ├── llm_client.py   # LLM客户端
│   │   └── file_ops.py     # 文件操作
│   ├── novel_manager.py    # 小说管理器
│   └── config.json         # 配置文件
├── novels/                 # 生成的小说目录
├── generate_content.py     # 交互式生成器
├── gen_batch.py            # 批量生成脚本
├── gen_chapter.py          # 单章生成脚本
├── main.py                 # 主入口
├── USER_GUIDE.md           # 用户指南
├── SPEC.md                 # 技术规格
└── .gitignore              # Git忽略配置
```

## 🚀 快速开始

```bash
# 安装依赖
pip install pyyaml requests

# 使用NVIDIA免费API
export NVIDIA_API_KEY="your-key"
python gen_batch.py
```

## 📖 更多信息

- 项目主页：[https://github.com/longjunjiu/AIxiaoshuo](https://github.com/longjunjiu/AIxiaoshuo)
- 用户指南：[USER_GUIDE.md](USER_GUIDE.md)
- 技术规格：[SPEC.md](SPEC.md)