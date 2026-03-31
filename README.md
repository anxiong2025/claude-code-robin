# claude-code-robin

> Read your codebase like Robin reads Poneglyphs.

A Python project architecture analyzer and documentation generator with built-in Claude AI conversation support.

## [Claude Code 核心代码泄漏详细剖析 — 完整架构深度解析（中英双语）](./ARCHITECTURE.md)

## Features

- **Project Scanning** — Recursively scan Python projects, count files/lines, discover modules
- **Dependency Analysis** — Parse AST to extract import relationships between modules
- **Architecture Reports** — Generate complete Markdown architecture documentation
- **Interactive Mode** — Chat with Claude about your codebase in the terminal
- **Dual AI Backend** — Supports both Anthropic API and AWS Bedrock

## Quick Start

```bash
# Install
pip install claude-code-robin

# Or install from source
git clone https://github.com/anxiong2025/claude-code-robin.git
cd claude-code-robin
pip install -e .
```

## Usage

```bash
# Scan a project
claude-code-robin scan ./my-project

# Generate full architecture report
claude-code-robin arch ./my-project

# Output report to file
claude-code-robin arch ./my-project -o ARCHITECTURE.md

# Analyze module dependencies
claude-code-robin deps ./my-project

# Print project statistics
claude-code-robin stats ./my-project

# Interactive mode (with Claude AI)
claude-code-robin interactive
```

### Interactive Mode

```
$ claude-code-robin interactive
claude-code-robin — Interactive Mode
Read your codebase like Robin reads Poneglyphs.

robin> scan ./src
robin> deps ./src
robin> What design patterns does this project use?   # → Claude conversation
robin> exit
```

### Programmatic Usage

```python
from src import scan_project, Reporter

# Scan and report
reporter = Reporter.from_path('./my-project')
print(reporter.render_full_report())

# Just scan
manifest = scan_project('./my-project')
print(f'Found {manifest.total_python_files} Python files')
print(manifest.to_markdown())
```

## Testing

```bash
python3 -m unittest discover -s tests -v
```

## Project Structure

```
claude-code-robin/
├── src/
│   ├── __init__.py       # Public API exports
│   ├── main.py           # CLI entrypoint & interactive REPL
│   ├── models.py         # Core data models (Module, Dependency, ProjectManifest, ArchReport)
│   ├── scanner.py        # Filesystem scanner & AST dependency analyzer
│   └── reporter.py       # Markdown report generator
├── tests/
│   └── test_porting_workspace.py
├── pyproject.toml        # Package configuration
├── LICENSE               # MIT License
└── README.md
```

## Architecture

```
main.py (CLI + REPL + Claude AI chat)
  └── reporter.py (report generation)
        └── scanner.py (filesystem scan + AST analysis)
              └── models.py (Module, Dependency, ProjectManifest, ArchReport)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key (for interactive mode) | — |
| `CLAUDE_CODE_USE_BEDROCK` | Set to `1` to use AWS Bedrock | disabled |
| `AWS_BEARER_TOKEN_BEDROCK` | AWS auth token for Bedrock | — |
| `AWS_REGION` | AWS region | `us-east-1` |

## License

MIT

---

## Author / 作者

![](https://fisherai-1312281807.cos.ap-guangzhou.myqcloud.com/6df7dfc5e5e5ea9267ed62795a992e4d.bmp)
