# claude-code-robin

> Read your codebase like Robin reads Poneglyphs.

A Python project architecture analyzer and documentation generator with built-in Claude AI conversation support.

## [Claude Code 核心代码泄漏详细剖析 — 完整架构深度解析（中英双语）](./ARCHITECTURE.md)

## Features

- **Project Scanning** — Recursively scan Python projects, count files/lines, discover modules
- **Dependency Analysis** — Parse AST to extract import relationships between modules
- **Architecture Reports** — Generate complete Markdown architecture documentation
- **Interactive Mode** — Chat with AI about your codebase in the terminal
- **15+ AI Providers** — Anthropic, OpenAI, Google, DeepSeek, 通义千问, 智谱, Kimi, OpenRouter...

## Quick Start

```bash
# 1. Install
git clone https://github.com/anxiong2025/claude-code-robin.git
cd claude-code-robin
pip install -e .

# 2. Configure API keys (interactive wizard)
claude-code-robin configure

# 3. Start chatting
claude-code-robin interactive
```

**Or skip configure — pass key directly:**

```bash
claude-code-robin interactive -p openrouter -k sk-or-v1-xxx
claude-code-robin interactive -p deepseek -k sk-xxx
claude-code-robin interactive -p anthropic -k sk-ant-xxx
```

## API Key Setup

### Option A: One-command wizard (recommended)

```bash
claude-code-robin configure
```

Prompts for each provider's key (press Enter to skip), saves to `~/.claude-code-robin/.env`.

### Option B: Command-line flags

```bash
claude-code-robin interactive -p <provider> -k <api-key> [-m <model>]
```

| Flag | Description |
|------|-------------|
| `-p, --provider` | Provider name (see table below) |
| `-k, --key` | API key |
| `-m, --model` | Model ID (optional, has defaults) |

### Option C: Environment variable

```bash
export OPENROUTER_API_KEY="sk-or-v1-xxx"
claude-code-robin interactive -p openrouter
```

### Supported Providers

| Provider (`-p`) | Default Model (`-m`) | Key Env Var | Get Key |
|-----------------|---------------------|-------------|---------|
| `anthropic` | `claude-sonnet-4-6-20250514` | `ANTHROPIC_API_KEY` | console.anthropic.com |
| `openai` | `gpt-4o` | `OPENAI_API_KEY` | platform.openai.com |
| `google` | `gemini-2.0-flash` | `GOOGLE_API_KEY` | aistudio.google.com |
| `openrouter` | `anthropic/claude-sonnet-4` | `OPENROUTER_API_KEY` | openrouter.ai |
| `groq` | `llama-3.3-70b-versatile` | `GROQ_API_KEY` | console.groq.com |
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

### Examples

```bash
# Anthropic Claude
claude-code-robin interactive -p anthropic -k sk-ant-xxx -m claude-opus-4-20250514

# OpenAI
claude-code-robin interactive -p openai -k sk-xxx -m gpt-4o-mini

# Google Gemini
claude-code-robin interactive -p google -k AIzaSyxxx

# DeepSeek
claude-code-robin interactive -p deepseek -k sk-xxx

# OpenRouter (one key, any model)
claude-code-robin interactive -p openrouter -k sk-or-xxx -m google/gemini-2.0-flash

# 通义千问
claude-code-robin interactive -p qwen -k sk-xxx

# 硅基流动
claude-code-robin interactive -p siliconflow -k sk-xxx -m Qwen/Qwen2.5-72B-Instruct
```

## Usage

```bash
# Scan a project
claude-code-robin scan ./my-project

# Generate full architecture report
claude-code-robin arch ./my-project -o ARCHITECTURE.md

# Analyze module dependencies
claude-code-robin deps ./my-project

# Print project statistics
claude-code-robin stats ./my-project

# List providers and key status
claude-code-robin models
```

### Interactive Mode

```
$ claude-code-robin interactive -p deepseek -k sk-xxx
claude-code-robin — Interactive Mode
Current: DeepSeek (深度求索) (deepseek, model: deepseek-chat)

robin> scan ./src
robin> What design patterns does this project use?
robin> model openrouter google/gemini-2.0-flash     # switch on the fly
robin> model                                         # show current
robin> models                                        # list all
robin> exit
```

### Programmatic Usage

```python
from src import scan_project, Reporter

reporter = Reporter.from_path('./my-project')
print(reporter.render_full_report())
```

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
claude-code-robin/
├── src/
│   ├── __init__.py       # Public API exports
│   ├── main.py           # CLI entrypoint & interactive REPL
│   ├── models.py         # Data models (Module, Dependency, ProjectManifest)
│   ├── scanner.py        # Filesystem scanner & AST dependency analyzer
│   ├── reporter.py       # Markdown report generator
│   ├── providers.py      # Multi-provider LLM abstraction (15+ providers)
│   └── config.py         # API key configuration management
├── tests/
│   └── test_porting_workspace.py
├── .env.example          # API key template
├── pyproject.toml
├── LICENSE
└── README.md
```

## License

MIT

---

## Author / 作者

![](https://fisherai-1312281807.cos.ap-guangzhou.myqcloud.com/6df7dfc5e5e5ea9267ed62795a992e4d.bmp)
