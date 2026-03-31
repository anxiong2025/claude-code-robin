# code-robin

> 像 Robin 阅读历史正文一样阅读你的代码。

Python 项目架构分析器 + 多模型 AI 对话终端工具。支持 15+ 国内外大模型厂商，一条命令配置，开箱即用。

## [Claude Code 核心代码泄漏详细剖析 — 完整架构深度解析（中英双语）](./ARCHITECTURE.md)

---

## 目录

- [项目架构](#项目架构)
- [快速开始](#快速开始)
- [API Key 配置](#api-key-配置)
- [支持的模型厂商](#支持的模型厂商)
- [使用示例](#使用示例)
- [命令参考](#命令参考)
- [编程接口](#编程接口)
- [测试](#测试)
- [许可证](#许可证)

---

## 项目架构

### 系统架构图

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              用户 (CLI)                                  │
│                                                                          │
│  code-robin configure          # 配置 API Key                     │
│  code-robin interactive -p deepseek -k sk-xxx   # AI 对话         │
│  code-robin scan ./src         # 扫描项目                         │
│  code-robin arch ./src         # 生成架构报告                      │
└──────────────────────┬───────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      main.py — 应用层 (CLI + REPL)                       │
│                                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │ argparse CLI │  │ Interactive  │  │  configure  │  │   models     │  │
│  │ 命令路由      │  │ REPL 交互    │  │  配置向导    │  │   厂商列表    │  │
│  └──────┬──────┘  └──────┬───────┘  └──────┬──────┘  └──────────────┘  │
│         │                │                  │                            │
└─────────┼────────────────┼──────────────────┼────────────────────────────┘
          │                │                  │
          ▼                ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌────────────────────────────────┐
│  reporter.py     │ │  providers.py    │ │  config.py                     │
│  报告生成器        │ │  多模型抽象层      │ │  配置管理                       │
│                  │ │                  │ │                                │
│ · render_manifest│ │ · Anthropic 原生  │ │ · load_env()  读取 .env        │
│ · render_stats   │ │ · OpenAI 兼容协议  │ │ · save_env()  写入 .env        │
│ · render_deps    │ │   (14 个厂商共用)  │ │ · configure_interactive()     │
│ · render_full    │ │ · chat_completion│ │ · 存储路径: ~/.code-robin│
│                  │ │ · detect_provider│ │                                │
└────────┬─────────┘ └──────────────────┘ └────────────────────────────────┘
         │
         ▼
┌──────────────────┐ ┌──────────────────┐
│  scanner.py      │ │  models.py       │
│  核心扫描引擎      │ │  数据模型          │
│                  │ │                  │
│ · scan_project() │ │ · Module         │
│   递归扫描 .py    │ │ · Dependency     │
│   统计文件/行数    │ │ · ProjectStats   │
│ · scan_deps()    │ │ · ProjectManifest│
│   AST 解析 import│ │ · ArchReport     │
└──────────────────┘ └──────────────────┘
```

### 模块职责

| 模块 | 职责 | 核心类/函数 |
|------|------|------------|
| `main.py` | CLI 入口、REPL 交互、命令路由 | `main()`, `interactive()`, `chat()` |
| `providers.py` | 15+ 大模型厂商的统一抽象层 | `ProviderConfig`, `chat_completion()`, `detect_provider()` |
| `config.py` | API Key 配置管理（读写 `~/.code-robin/.env`） | `configure_interactive()`, `load_env()`, `save_env()` |
| `reporter.py` | Markdown 报告生成 | `Reporter.render_full_report()` |
| `scanner.py` | 文件系统扫描 + AST 依赖分析 | `scan_project()`, `scan_dependencies()` |
| `models.py` | 不可变数据模型 | `Module`, `Dependency`, `ProjectManifest` |

### 数据流

```
用户输入 → main.py 解析命令
  ├── scan/arch/deps/stats → scanner.py 扫描 → reporter.py 渲染 → Markdown 输出
  ├── 对话文本 → providers.py → 厂商 API → AI 回复
  └── configure → config.py → ~/.code-robin/.env
```

### 多模型架构设计

```
providers.py
  │
  ├── Anthropic ──→ anthropic SDK (原生协议)
  │
  └── 其他 14 个厂商 ──→ httpx + OpenAI 兼容协议
        │
        ├── OpenAI      → api.openai.com/v1
        ├── Google      → generativelanguage.googleapis.com
        ├── OpenRouter   → openrouter.ai/api/v1        (聚合平台，一个 key 用所有模型)
        ├── DeepSeek    → api.deepseek.com/v1
        ├── 智谱 AI      → open.bigmodel.cn/api/paas/v4
        ├── 通义千问      → dashscope.aliyuncs.com
        ├── 月之暗面      → api.moonshot.cn/v1
        ├── 百川智能      → api.baichuan-ai.com/v1
        ├── MiniMax     → api.minimax.chat/v1
        ├── 零一万物      → api.lingyiwanwu.com/v1
        ├── 硅基流动      → api.siliconflow.cn/v1
        ├── 阶跃星辰      → api.stepfun.com/v1
        ├── 讯飞星火      → spark-api-open.xf-yun.com/v1
        └── Groq        → api.groq.com/openai/v1
```

### 目录结构

```
code-robin/
├── src/
│   ├── __init__.py       # 公开 API 导出
│   ├── main.py           # CLI 入口 + REPL 交互模式
│   ├── providers.py      # 多模型厂商统一抽象层 (15+ 厂商)
│   ├── config.py         # API Key 配置管理
│   ├── models.py         # 数据模型 (Module, Dependency, ProjectManifest...)
│   ├── scanner.py        # 文件扫描 + AST 依赖分析引擎
│   └── reporter.py       # Markdown 报告生成器
├── tests/
│   └── test_porting_workspace.py   # 12 个单元测试
├── .env.example          # API Key 配置模板
├── pyproject.toml        # 项目配置 (Python 3.11+)
├── ARCHITECTURE.md       # 详细架构文档（中英双语）
├── LICENSE               # MIT 许可证
└── README.md
```

---

## 快速开始

### 环境要求

- Python 3.11+（推荐 3.13）
- pip 或 uv

检查 Python 版本：

```bash
python3 --version   # 需要 3.11 或以上
```

### 第一步：克隆项目

```bash
git clone https://github.com/anxiong2025/code-robin.git
cd code-robin
```

### 第二步：创建虚拟环境并安装

```bash
# 创建虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 安装项目（开发模式）
pip install -e .
```

> 激活后终端提示符会出现 `(.venv)`，表示虚拟环境已生效。

### 第三步：启动

```bash
# 直接传入 Key 启动（以 DeepSeek 为例）
code-robin interactive -p deepseek -k sk-你的key

# 或者用 OpenRouter（一个 key 用所有模型）
code-robin interactive -p openrouter -k sk-or-v1-xxx

# 或者用 Anthropic Claude
code-robin interactive -p anthropic -k sk-ant-xxx
```

就这三步，可以开聊了。

### 持久化保存 Key（可选）

不想每次都传 `-k`？运行配置向导：

```bash
code-robin configure    # 交互式输入各厂商 Key，按 Enter 跳过不需要的

# 以后直接启动
code-robin interactive
```

### 不激活虚拟环境也能用

如果你不想每次 `source .venv/bin/activate`，可以直接用完整路径：

```bash
.venv/bin/code-robin interactive -p deepseek -k sk-你的key
```

---

## API Key 配置

有三种方式配置 API Key，任选其一：

### 方式一：命令行直接传入（最快）

```bash
code-robin interactive -p <厂商> -k <你的key> [-m <模型>]
```

| 参数 | 说明 |
|------|------|
| `-p, --provider` | 厂商名称（见下表） |
| `-k, --key` | API Key |
| `-m, --model` | 模型 ID（可选，每个厂商有默认值） |

### 方式二：配置向导（推荐长期使用）

```bash
code-robin configure
```

交互式逐个提示输入各厂商 Key（按 Enter 跳过），最后选择默认厂商。配置保存到 `~/.code-robin/.env`。

### 方式三：环境变量

```bash
export DEEPSEEK_API_KEY="sk-你的key"
code-robin interactive -p deepseek
```

也可以手动创建配置文件：

```bash
mkdir -p ~/.code-robin
cat > ~/.code-robin/.env << 'EOF'
DEEPSEEK_API_KEY=sk-你的key
DEFAULT_PROVIDER=deepseek
EOF
```

---

## 支持的模型厂商

### 国际厂商

| 厂商 (`-p`) | 默认模型 (`-m`) | 环境变量 | 申请地址 |
|-------------|----------------|---------|---------|
| `anthropic` | `claude-sonnet-4-6-20250514` | `ANTHROPIC_API_KEY` | console.anthropic.com |
| `openai` | `gpt-4o` | `OPENAI_API_KEY` | platform.openai.com |
| `google` | `gemini-2.0-flash` | `GOOGLE_API_KEY` | aistudio.google.com |
| `openrouter` | `anthropic/claude-sonnet-4` | `OPENROUTER_API_KEY` | openrouter.ai |
| `groq` | `llama-3.3-70b-versatile` | `GROQ_API_KEY` | console.groq.com |

### 国内厂商

| 厂商 (`-p`) | 默认模型 (`-m`) | 环境变量 | 申请地址 |
|-------------|----------------|---------|---------|
| `deepseek` | `deepseek-chat` | `DEEPSEEK_API_KEY` | platform.deepseek.com |
| `zhipu` | `glm-4-flash` | `ZHIPU_API_KEY` | open.bigmodel.cn |
| `qwen` | `qwen-plus` | `DASHSCOPE_API_KEY` | dashscope.console.aliyun.com |
| `moonshot` | `moonshot-v1-8k` | `MOONSHOT_API_KEY` | platform.moonshot.cn |
| `baichuan` | `Baichuan4-Air` | `BAICHUAN_API_KEY` | platform.baichuan-ai.com |
| `minimax` | `MiniMax-Text-01` | `MINIMAX_API_KEY` | platform.minimaxi.com |
| `yi` | `yi-lightning` | `YI_API_KEY` | platform.lingyiwanwu.com |
| `siliconflow` | `deepseek-ai/DeepSeek-V3` | `SILICONFLOW_API_KEY` | siliconflow.cn |
| `stepfun` | `step-2-16k` | `STEPFUN_API_KEY` | platform.stepfun.com |
| `spark` | `generalv3.5` | `SPARK_API_KEY` | xinghuo.xfyun.cn |

> **提示**：OpenRouter 是聚合平台，一个 Key 就能调用所有模型（Claude、GPT、Gemini、Llama 等），适合想要灵活切换的用户。

---

## 使用示例

```bash
# 各厂商启动示例
code-robin interactive -p deepseek -k sk-xxx
code-robin interactive -p openai -k sk-xxx -m gpt-4o-mini
code-robin interactive -p google -k AIzaSyxxx
code-robin interactive -p qwen -k sk-xxx -m qwen-max
code-robin interactive -p openrouter -k sk-or-xxx -m google/gemini-2.0-flash

# 项目分析
code-robin scan ./my-project                    # 扫描项目结构
code-robin arch ./my-project -o ARCHITECTURE.md  # 生成架构报告
code-robin deps ./my-project                    # 模块依赖分析
code-robin stats ./my-project                   # 项目统计
code-robin models                               # 查看厂商及 Key 状态
```

### 交互模式

```
$ code-robin interactive -p deepseek -k sk-xxx
code-robin — Interactive Mode
Current: DeepSeek (深度求索) (deepseek, model: deepseek-chat)

robin> scan ./src                                   # 扫描项目
robin> 这个项目用了什么设计模式？                        # AI 对话
robin> model openrouter google/gemini-2.0-flash      # 切换厂商和模型
robin> model                                         # 查看当前模型
robin> models                                        # 列出所有厂商
robin> exit
```

---

## 命令参考

| 命令 | 说明 |
|------|------|
| `configure` | 交互式配置 API Key 向导 |
| `interactive [-p] [-k] [-m]` | AI 对话交互模式 |
| `models` | 列出所有厂商及 Key 状态 |
| `scan [path]` | 扫描 Python 项目结构 |
| `arch [path] [-o file]` | 生成完整架构报告 |
| `deps [path]` | 分析模块依赖关系 |
| `stats [path]` | 输出项目统计信息 |

### 交互模式内部命令

| 命令 | 说明 |
|------|------|
| `model` | 查看当前使用的厂商和模型 |
| `model <厂商> [模型]` | 切换厂商和模型 |
| `models` | 列出所有厂商 |
| `scan/arch/deps/stats [path]` | 项目分析（同 CLI 命令） |
| `help` | 显示帮助 |
| `exit` / `quit` | 退出 |
| 其他文本 | 发送给 AI 对话 |

---

## 编程接口

```python
from src import scan_project, Reporter

manifest = scan_project('./my-project')
print(reporter := Reporter.from_path('./my-project'))
print(reporter.render_full_report())
```

## 测试

```bash
source .venv/bin/activate
pytest tests/ -v    # 12 个测试
```

---

## 许可证

MIT

---

## 免责声明

本项目基于公开泄漏的 Claude Code 源码进行学习研究与架构分析，仅供教育和技术交流目的。

- 本项目**不声明**对 Claude Code 原始源码的任何所有权
- 本项目与 [Anthropic](https://www.anthropic.com/) **没有任何关联**，未获得其赞助、认可或授权
- Claude Code 的所有权利归 Anthropic 所有
- 如有侵权，请联系删除

> This project is based on publicly leaked Claude Code source code for educational and architectural analysis purposes only. It is not affiliated with, endorsed by, or maintained by Anthropic. All rights to Claude Code belong to Anthropic.

---

## 作者

![](https://fisherai-1312281807.cos.ap-guangzhou.myqcloud.com/6df7dfc5e5e5ea9267ed62795a992e4d.bmp)
