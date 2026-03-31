# code-robin — Complete Project Architecture / 完整项目架构分析

![](https://fisherai-1312281807.cos.ap-guangzhou.myqcloud.com/e5ccbf0d9b6a5440cd550c8f99beceda.png)

> **Read your codebase like Robin reads Poneglyphs.**
>
> **像 Robin 阅读历史正文一样阅读你的代码。**

---

# Table of Contents / 目录

- [Overall Architecture / 整体架构总览](#overall-architecture--整体架构总览)
- [Quick Start / 快速开始](#quick-start--快速开始)
- [1. Project Overview / 项目概述](#1-project-overview--项目概述)
- [2. Tech Stack / 技术栈](#2-tech-stack--技术栈)
- [3. Project Structure / 项目结构](#3-project-structure--项目结构)
- [4. Core Modules Deep Dive / 核心模块深度解析](#4-core-modules-deep-dive--核心模块深度解析)
  - [4.1 models.py — Data Models / 数据模型](#41-modelspy--data-models--数据模型基础层)
  - [4.2 scanner.py — Core Engine / 核心引擎](#42-scannerpy--core-engine--核心引擎文件系统--ast-层)
  - [4.3 reporter.py — Report Generator / 报告生成器](#43-reporterpy--report-generator--报告生成器聚合层)
  - [4.4 main.py — CLI & Interactive Shell / 命令行与交互模式](#44-mainpy--cli--interactive-shell--命令行与交互模式应用层)
  - [4.5 \_\_init\_\_.py — Public API / 公开接口](#45-__init__py--public-api--公开接口)
- [5. Claude AI Integration / AI 集成架构](#5-claude-ai-integration--ai-集成架构)
- [6. Testing / 测试体系](#6-testing--测试体系)
- [7. Configuration / 配置说明](#7-configuration--配置说明)
- [8. Extension Guide / 扩展指南](#8-extension-guide--扩展指南)
- [9. Design Decisions / 设计决策](#9-design-decisions--设计决策)
- [Author / 作者](#author--作者)

---

# Overall Architecture / 整体架构总览

## System Architecture Diagram / 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER / 用户                               │
│                                                                 │
│   $ code-robin scan ./src                                │
│   $ code-robin arch ./src -o report.md                   │
│   $ code-robin interactive                               │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     main.py (Application Layer / 应用层)         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │  CLI Parser   │  │ Interactive  │  │  Claude AI Chat    │    │
│  │  (argparse)   │  │ REPL (robin>)│  │  (dual backend)    │    │
│  │              │  │              │  │                    │    │
│  │  scan        │  │  known cmd   │  │  Anthropic API     │    │
│  │  arch [-o]   │  │  → local exec│  │       or           │    │
│  │  deps        │  │              │  │  AWS Bedrock       │    │
│  │  stats       │  │  other text  │  │                    │    │
│  │  interactive │  │  → AI chat   │  │  System Prompt:    │    │
│  └──────┬───────┘  └──────┬───────┘  │  "You are Robin"   │    │
│         │                 │          └────────────────────┘    │
│         └────────┬────────┘                                    │
│                  │                                              │
└──────────────────┼──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                  reporter.py (Aggregation Layer / 聚合层)        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Reporter                              │   │
│  │                                                         │   │
│  │  .from_path(path)     ← Factory: scan + analyze         │   │
│  │  .render_manifest()   ← Project structure overview       │   │
│  │  .render_stats()      ← Statistics table                 │   │
│  │  .render_dependencies() ← Grouped import analysis        │   │
│  │  .render_full_report()  ← All sections → ArchReport      │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                  scanner.py (Core Engine / 核心引擎层)            │
│                                                                 │
│  ┌───────────────────────┐  ┌────────────────────────────┐     │
│  │   scan_project(root)  │  │  scan_dependencies(root)   │     │
│  │                       │  │                            │     │
│  │  1. rglob('*.py')     │  │  1. ast.parse(each file)   │     │
│  │  2. Counter(modules)  │  │  2. ast.walk(tree)         │     │
│  │  3. count lines       │  │  3. extract Import nodes   │     │
│  │  4. → ProjectManifest │  │  4. extract ImportFrom     │     │
│  │     ├── modules       │  │  5. → list[Dependency]     │     │
│  │     └── stats         │  │     ├── source             │     │
│  └───────────────────────┘  │     ├── target             │     │
│                             │     └── import_type        │     │
│                             └────────────────────────────┘     │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                  models.py (Foundation Layer / 基础层)            │
│                                                                 │
│  ┌────────────┐ ┌────────────┐ ┌──────────────┐               │
│  │   Module    │ │ Dependency │ │ ProjectStats │               │
│  │  (frozen)   │ │  (frozen)  │ │   (frozen)   │               │
│  └────────────┘ └────────────┘ └──────────────┘               │
│  ┌──────────────────┐  ┌────────────────┐                     │
│  │ ProjectManifest   │  │  ArchReport    │                     │
│  │  .to_markdown()   │  │  .render()     │                     │
│  └──────────────────┘  └────────────────┘                     │
│                                                                 │
│  Zero internal dependencies — stdlib only (dataclasses, pathlib)│
│  零内部依赖 — 仅使用标准库                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Layered Architecture / 分层架构

```
Layer 4 — Application   │ main.py        │ CLI parsing, REPL, AI chat, user I/O
         应用层          │                │ 命令解析、交互式终端、AI 对话、用户 I/O
─────────────────────────┼────────────────┼─────────────────────────────────────
Layer 3 — Aggregation    │ reporter.py    │ Combine scan results into Markdown reports
         聚合层          │                │ 将扫描结果组合为 Markdown 报告
─────────────────────────┼────────────────┼─────────────────────────────────────
Layer 2 — Core Engine    │ scanner.py     │ Filesystem scanning + AST dependency analysis
         核心引擎层       │                │ 文件系统扫描 + AST 依赖分析
─────────────────────────┼────────────────┼─────────────────────────────────────
Layer 1 — Foundation     │ models.py      │ Data models (Module, Dependency, Manifest...)
         基础层          │                │ 数据模型定义
```

**Rule: each layer only imports from the layer directly below it. / 规则：每层只导入下一层。**

## Complete Data Flow / 完整数据流

```
         User specifies a Python project directory
         用户指定 Python 项目目录
                     │
                     ▼
  ┌──────────────────────────────────┐
  │          scanner.py              │
  │                                  │
  │  scan_project(root)              │
  │    ├── Path.rglob('*.py')        │───→ file list / 文件列表
  │    ├── Counter(modules)          │───→ module counts / 模块计数
  │    ├── sum(lines per file)       │───→ total lines / 总行数
  │    └── → ProjectManifest         │
  │          ├── .root               │
  │          ├── .total_python_files  │
  │          ├── .modules: tuple     │
  │          └── .stats: ProjectStats│
  │                                  │
  │  scan_dependencies(root)         │
  │    ├── ast.parse(each .py)       │
  │    ├── ast.walk(tree)            │
  │    ├── classify Import nodes     │
  │    └── → list[Dependency]        │
  │          ├── .source             │
  │          ├── .target             │
  │          └── .import_type        │
  └──────────────┬───────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────┐
  │          reporter.py             │
  │                                  │
  │  Reporter(manifest, deps)        │
  │    ├── render_manifest()   ──────│──→ Markdown: project structure
  │    ├── render_stats()      ──────│──→ Markdown: statistics table
  │    ├── render_dependencies()─────│──→ Markdown: grouped imports
  │    └── render_full_report()──────│──→ Markdown: all combined
  │         └── ArchReport.render()  │
  └──────────────┬───────────────────┘
                 │
                 ▼
  ┌──────────────────────────────────┐
  │           main.py                │
  │                                  │
  │  CLI mode / CLI 模式:            │
  │    scan  → render_manifest() ────│──→ stdout
  │    arch  → render_full_report()──│──→ stdout or file (-o)
  │    deps  → render_dependencies()─│──→ stdout
  │    stats → render_stats()   ─────│──→ stdout
  │                                  │
  │  Interactive / 交互模式:          │
  │    known cmd → run_command() ────│──→ stdout (local, no API)
  │    other text → chat()     ──────│──→ Claude AI → stdout
  └──────────────────────────────────┘
```

## Module Dependency Graph / 模块依赖关系图

```
┌─────────────────────────────────────────────────┐
│                   main.py                        │
│         (CLI + REPL + Claude AI chat)            │
│       [argparse, os, shlex, pathlib]             │
│       [anthropic*, httpx*, json*]  (* = lazy)    │
└──────────────────┬──────────────────────────────┘
                   │ imports / 导入
                   ▼
          ┌──────────────────┐
          │   reporter.py     │
          │  (Report engine)  │
          │  [pathlib]        │
          └────────┬─────────┘
                   │ imports / 导入
                   ▼
          ┌──────────────────┐
          │   scanner.py      │
          │  (FS + AST)       │
          │  [ast, Counter,   │
          │   pathlib]        │
          └────────┬─────────┘
                   │ imports / 导入
                   ▼
          ┌──────────────────┐
          │   models.py       │
          │  (Data models)    │
          │  [dataclasses,    │
          │   pathlib]        │
          └──────────────────┘

Linear chain, zero circular imports.
线性链条，零循环依赖。
```

## Actual Import Map (self-scan result) / 实际 Import 映射（自扫描结果）

```
__init__  → models (relative), reporter (relative), scanner (relative)
main      → reporter (relative), scanner (relative)
            + argparse, os, shlex, pathlib (stdlib)
            + anthropic, httpx, json (lazy import, for AI chat only)
reporter  → models (relative), scanner (relative), pathlib (stdlib)
scanner   → models (relative), ast, collections, pathlib (stdlib)
models    → dataclasses, pathlib (stdlib only — zero internal deps)
```

---

# Quick Start / 快速开始

## Installation / 安装

```bash
git clone https://github.com/anxiong2025/code-robin.git
cd code-robin

# Create virtual environment / 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install in editable mode / 以开发模式安装
pip install -e .

# Optional: install Bedrock support / 可选：安装 Bedrock 支持
pip install -e ".[bedrock]"
```

## Run / 启动

```bash
# Scan a project / 扫描项目
code-robin scan ./src

# Generate architecture report / 生成架构报告
code-robin arch ./src

# Write report to file / 输出报告到文件
code-robin arch ./src -o report.md

# Analyze dependencies / 分析依赖
code-robin deps ./src

# Project statistics / 项目统计
code-robin stats ./src

# Interactive mode with Claude AI / 交互模式（支持 Claude AI 对话）
code-robin interactive
```

## Run without install / 不安装直接运行

```bash
python3 -m src.main scan ./src
python3 -m src.main arch ./src
python3 -m src.main interactive
```

## Run Tests / 运行测试

```bash
# All tests / 全部测试
python3 -m unittest discover -s tests -v

# Single test class / 单个测试类
python3 -m unittest tests.test_porting_workspace.ScannerTests -v

# Single test method / 单个测试方法
python3 -m unittest tests.test_porting_workspace.CLITests.test_cli_scan_runs
```

## Interactive Mode Demo / 交互模式演示

```
$ code-robin interactive

code-robin — Interactive Mode
Read your codebase like Robin reads Poneglyphs.
Type "help" for available commands, "exit" to quit.
Other input will be sent to Claude for conversation.

robin> help
Available commands:
  scan [path]              scan a Python project and print manifest
  arch [path]              generate full architecture report
  deps [path]              analyze and print module dependencies
  stats [path]             print project statistics
  help                     show this help message
  exit / quit              exit the interactive shell

robin> scan ./src
## Project Manifest
Root: `/path/to/src`
Total Python files: **5**
...

robin> What design patterns does this project use?
→ Claude AI responds with architecture analysis...

robin> exit
```

---

# 1. Project Overview / 项目概述

**English:**

code-robin is a Python project architecture analyzer and documentation generator. It scans Python codebases, analyzes module dependencies via AST parsing, computes statistics, and generates comprehensive Markdown architecture reports. It also provides an interactive mode powered by Claude AI for natural-language conversations about your codebase.

Inspired by Nico Robin from One Piece — the archaeologist who reads Poneglyphs (ancient stone tablets) to uncover hidden history. This tool reads your code to uncover its hidden structure.

**中文：**

code-robin 是一个 Python 项目架构分析器和文档生成器。它扫描 Python 代码库，通过 AST 解析分析模块依赖关系，计算代码统计数据，并生成完整的 Markdown 架构报告。还提供由 Claude AI 驱动的交互模式，支持用自然语言询问代码结构。

灵感来自《海贼王》的 Nico Robin —— 考古学家，专门阅读历史正文（Poneglyphs）来揭示隐藏的历史。这个工具读的是你的代码，揭示的是代码的隐藏结构。

### Project Stats / 项目数据

| Metric / 指标 | Value / 值 |
|---------------|-----------|
| Python modules / 模块数 | 5 |
| Lines of code / 代码行数 | 434 (src), 536 (total with tests) |
| Test cases / 测试用例 | 12 |
| CLI commands / CLI 命令 | 5 (scan, arch, deps, stats, interactive) |
| AI backends / AI 后端 | 2 (Anthropic API, AWS Bedrock) |
| License / 许可证 | MIT |
| Python version / 版本要求 | >= 3.11 |

---

# 2. Tech Stack / 技术栈

| Category / 类别 | Technology / 技术 | Purpose / 用途 |
|-----------------|-------------------|---------------|
| Language / 语言 | Python >= 3.11 | Core runtime / 核心运行时 |
| AST Analysis / 语法分析 | `ast` (stdlib) | Parse imports / 解析 import 语句 |
| File Scanning / 文件扫描 | `pathlib` (stdlib) | Recursive file discovery / 递归文件发现 |
| Statistics / 统计 | `collections.Counter` (stdlib) | Module file counting / 模块文件计数 |
| Data Modeling / 数据建模 | `dataclasses` (stdlib) | Type-safe data structures / 类型安全的数据结构 |
| CLI / 命令行 | `argparse` (stdlib) | Command parsing / 命令解析 |
| Shell Parsing / 命令拆分 | `shlex` (stdlib) | REPL input tokenization / REPL 输入分词 |
| AI (direct) | `anthropic` SDK | Claude Messages API / Claude 消息 API |
| AI (cloud) | `httpx` | AWS Bedrock REST calls / Bedrock REST 调用 |
| Testing / 测试 | `unittest` (stdlib) | Unit + integration tests / 单元 + 集成测试 |
| Packaging / 打包 | `setuptools` | pip installable package / pip 可安装包 |

**Zero required binary dependencies. / 零必需二进制依赖。**

---

# 3. Project Structure / 项目结构

```
code-robin/
│
├── src/                              # Core source package / 核心源码包
│   ├── __init__.py                   #   Public API exports / 公开 API 导出 (16 lines)
│   ├── models.py                     #   Data models / 数据模型 (67 lines)
│   ├── scanner.py                    #   FS scan + AST analysis / 文件扫描 + AST 分析 (83 lines)
│   ├── reporter.py                   #   Markdown report engine / 报告生成引擎 (74 lines)
│   └── main.py                       #   CLI + REPL + AI chat / 命令行 + 交互 + AI 对话 (194 lines)
│
├── tests/
│   └── test_porting_workspace.py     # 12 test cases / 12 个测试用例 (102 lines)
│
├── pyproject.toml                    # Package config / 包配置
├── LICENSE                           # MIT License
├── README.md                         # Project README
└── ARCHITECTURE.md                   # This file / 本文件
```

**Total: 5 modules, 434 lines of source code, 102 lines of tests.**

**合计：5 个模块，434 行源码，102 行测试代码。**

---

# 4. Core Modules Deep Dive / 核心模块深度解析

## 4.1 `models.py` — Data Models / 数据模型（基础层）

**English:** The foundation layer. Defines 5 dataclasses used by all other modules. Zero internal dependencies — only imports `dataclasses` and `pathlib` from stdlib.

**中文：** 项目的最底层模块，被所有其他模块依赖。定义 5 个 dataclass，构成整个项目的类型基础。零内部依赖，仅使用标准库。

### `Module` (frozen dataclass / 不可变数据类)

Represents a discovered Python module in the scanned project.

描述扫描发现的一个 Python 模块。

```python
@dataclass(frozen=True)
class Module:
    name: str           # Module name, e.g. "main.py" or "utils" (directory)
                        # 模块名，如 "main.py"（单文件）或 "utils"（目录）
    path: str           # Full path to the module
                        # 模块完整路径
    file_count: int     # Number of .py files in this module
                        # 该模块下 .py 文件数量
    description: str = ''  # Optional description (not set by scanner)
                           # 可选描述（scanner 不设置，留给扩展）
```

**Design notes / 设计要点：**
- `frozen=True` makes instances immutable and hashable — safe to store in tuples
- `frozen=True` 使实例不可变且可哈希 — 可安全存入 tuple
- `description` defaults to `''` — scanner doesn't populate it, keeping the model generic
- `description` 默认空字符串 — scanner 不填充，保持模型通用性

### `Dependency` (frozen dataclass / 不可变数据类)

Represents an import relationship between two modules.

描述两个模块之间的 import 依赖关系。

```python
@dataclass(frozen=True)
class Dependency:
    source: str         # Module that contains the import statement
                        # 包含 import 语句的模块
    target: str         # Module/package being imported
                        # 被 import 的模块/包
    import_type: str = 'absolute'  # 'absolute' | 'relative' | 'third_party'
                                   # 导入类型
```

**Classification rules / 分类规则：**

| `import_type` | Trigger / 触发条件 | Example / 示例 |
|---------------|-------------------|---------------|
| `relative` | `node.level > 0` (dot imports) | `from .models import Module` |
| `absolute` | `node.level == 0` with module name | `import ast`, `from pathlib import Path` |

**Example instances / 实例化示例：**
```python
Dependency(source='main', target='reporter', import_type='relative')
Dependency(source='scanner', target='ast', import_type='absolute')
Dependency(source='reporter', target='models', import_type='relative')
```

### `ProjectStats` (frozen dataclass / 不可变数据类)

Aggregate statistics for a scanned project.

项目级聚合统计。

```python
@dataclass(frozen=True)
class ProjectStats:
    total_files: int          # Total .py files / .py 文件总数
    total_lines: int          # Total lines of code / 代码总行数
    total_modules: int        # Top-level module count / 顶层模块数
    avg_lines_per_file: float # Average lines per file / 平均每文件行数
```

### `ProjectManifest` — Complete scan result / 完整扫描结果

The main output of `scan_project()`. Contains everything discovered about the project.

`scan_project()` 的主要输出，包含项目的所有发现信息。

```python
@dataclass
class ProjectManifest:
    root: Path                              # Project root directory / 项目根目录
    total_python_files: int                 # .py file count / .py 文件总数
    modules: tuple[Module, ...] = ()        # Discovered modules (sorted by file count desc)
                                            # 发现的模块（按文件数降序排列）
    stats: ProjectStats | None = None       # Aggregate statistics / 聚合统计
```

**`to_markdown()` output example / 输出示例：**
```markdown
## Project Manifest

Root: `/path/to/src`
Total Python files: **5**
Total lines: **434**
Average lines per file: **86.8**

Modules:
- `scanner.py` (1 files)
- `models.py` (1 files)
- `reporter.py` (1 files)
- `__init__.py` (1 files)
- `main.py` (1 files)
```

**Rendering logic / 渲染逻辑：**
1. Always outputs root path and file count / 始终输出根路径和文件数
2. If `stats` is not None, appends total lines and average / 如果 `stats` 非空，追加行数和平均值
3. Lists each module with file count and optional description / 列出每个模块的文件数和可选描述

### `ArchReport` — Report container / 报告容器

Combines a title with multiple Markdown sections into a single report.

将标题和多个 Markdown 段落组合为一份完整报告。

```python
@dataclass
class ArchReport:
    title: str                                          # Report title / 报告标题
    sections: list[str] = field(default_factory=list)   # Markdown sections / Markdown 段落列表

    def render(self) -> str:
        return '\n\n'.join([f'# {self.title}', *self.sections])
        # Joins title + all sections with double newlines
        # 用双换行拼接标题和所有段落
```

---

## 4.2 `scanner.py` — Core Engine / 核心引擎（文件系统 + AST 层）

**English:** The core analysis engine. Contains two independent functions: one for filesystem scanning, one for AST-based dependency extraction. This is the only module that touches the filesystem and parses Python source code.

**中文：** 核心分析引擎。包含两个独立函数：一个负责文件系统扫描，一个负责基于 AST 的依赖提取。这是唯一与文件系统交互并解析 Python 源码的模块。

**Dependencies / 依赖：** `ast`, `collections.Counter`, `pathlib.Path`, `.models`

### Function 1: `scan_project(root) → ProjectManifest`

**Signature / 签名：**
```python
def scan_project(root: Path | str) -> ProjectManifest
```

**Parameters / 参数：**
- `root` — Project directory to scan. Accepts `str` or `Path`, converted to absolute path internally.
- `root` — 要扫描的项目目录。接受 `str` 或 `Path`，内部转为绝对路径。

**Returns / 返回：** `ProjectManifest` with modules, stats, and metadata.

**Raises / 异常：** `ValueError` if `root` is not a directory / 如果 `root` 不是目录则抛出 `ValueError`。

**Step-by-step execution flow / 逐步执行流程：**

```
Step 1: Resolve path / 解析路径
│  root = Path(root).resolve()
│  if not root.is_dir(): raise ValueError
│
Step 2: Collect Python files / 收集 Python 文件
│  files = [p for p in root.rglob('*.py')
│           if p.is_file() and '__pycache__' not in p.parts]
│  └── rglob recursively finds all .py files
│  └── Excludes __pycache__ directories
│
Step 3: Count files per module / 按模块统计文件数
│  counter = Counter()
│  for path in files:
│      rel = path.relative_to(root)
│      key = rel.parts[0] if len(rel.parts) > 1 else rel.name
│      counter[key] += 1
│
Step 4: Count total lines / 统计总行数
│  for path in files:
│      total_lines += len(path.read_text('utf-8').splitlines())
│  └── Silently skips files with OSError or UnicodeDecodeError
│
Step 5: Build Module tuples / 构建 Module 元组
│  modules = tuple(Module(...) for name, count in counter.most_common())
│  └── Sorted by file count descending
│
Step 6: Build ProjectStats / 构建统计信息
│  avg = total_lines / len(files) if files else 0.0
│  stats = ProjectStats(total_files=..., total_lines=..., ...)
│
Step 7: Return ProjectManifest / 返回清单
│  return ProjectManifest(root=root, total_python_files=len(files), ...)
```

**Module attribution logic / 模块归属判断：**

```python
# File: /project/src/main.py
# relative_to(root) → PurePath('main.py')
# parts = ('main.py',) → len == 1 → key = 'main.py' (single-file module)

# File: /project/src/utils/helper.py
# relative_to(root) → PurePath('utils/helper.py')
# parts = ('utils', 'helper.py') → len == 2 → key = 'utils' (directory module)

# File: /project/src/utils/parser.py
# Same → key = 'utils' → counter['utils'] = 2
```

### Function 2: `scan_dependencies(root) → list[Dependency]`

**Signature / 签名：**
```python
def scan_dependencies(root: Path | str) -> list[Dependency]
```

**Parameters / 参数：**
- `root` — Same as `scan_project`. / 同 `scan_project`。

**Returns / 返回：** List of all import dependencies found across all `.py` files.

**Step-by-step execution flow / 逐步执行流程：**

```
Step 1: Collect .py files / 收集文件
│  (Same filtering as scan_project)
│
Step 2: For each file / 对每个文件:
│  ├── Read source text / 读取源码
│  │   source_text = path.read_text('utf-8')
│  │
│  ├── Parse AST / 解析语法树
│  │   tree = ast.parse(source_text, filename=str(path))
│  │   └── Skips files with SyntaxError / 跳过语法错误的文件
│  │
│  ├── Determine source module name / 确定源模块名
│  │   source_name = parts[0] if directory else path.stem
│  │   └── Uses .stem (no .py extension) for consistency
│  │
│  └── Walk AST nodes / 遍历 AST 节点:
│      │
│      ├── ast.Import node / Import 节点
│      │   Example: import os, json
│      │   → Dependency(source, 'os', 'absolute')
│      │   → Dependency(source, 'json', 'absolute')
│      │
│      └── ast.ImportFrom node / ImportFrom 节点
│          │
│          ├── node.level > 0 (relative import / 相对导入)
│          │   Example: from .models import Module
│          │   → Dependency(source, 'models', 'relative')
│          │
│          └── node.level == 0 (absolute import / 绝对导入)
│              Example: from pathlib import Path
│              → Dependency(source, 'pathlib', 'absolute')
```

**AST parsing examples / AST 解析示例：**

| Source code / 源代码 | AST node / 节点 | Result / 结果 |
|---------------------|-----------------|--------------|
| `import ast` | `Import(names=[alias(name='ast')])` | `Dependency('scanner', 'ast', 'absolute')` |
| `from .models import Module` | `ImportFrom(module='models', level=1)` | `Dependency('scanner', 'models', 'relative')` |
| `from pathlib import Path` | `ImportFrom(module='pathlib', level=0)` | `Dependency('scanner', 'pathlib', 'absolute')` |
| `from collections import Counter` | `ImportFrom(module='collections', level=0)` | `Dependency('scanner', 'collections', 'absolute')` |
| `import json` (inside function) | `Import(names=[alias(name='json')])` | `Dependency('main', 'json', 'absolute')` |

**Error handling / 错误处理：**
- `OSError` → skip file / 跳过文件（文件不可读）
- `SyntaxError` → skip file / 跳过文件（Python 语法错误）
- `UnicodeDecodeError` → skip file / 跳过文件（编码问题）

All errors are silently caught — one bad file doesn't break the entire scan.

所有错误静默捕获 — 一个坏文件不会中断整个扫描。

---

## 4.3 `reporter.py` — Report Generator / 报告生成器（聚合层）

**English:** The aggregation layer. Takes raw data from scanner and transforms it into human-readable Markdown reports. This is the bridge between scanner output and CLI output.

**中文：** 聚合层。将 scanner 的原始数据转化为人类可读的 Markdown 报告。是 scanner 输出和 CLI 输出之间的桥梁。

**Dependencies / 依赖：** `.models`, `.scanner`

### `Reporter` class / Reporter 类

```python
class Reporter:
    def __init__(self, manifest: ProjectManifest, dependencies: list[Dependency] | None = None):
        self.manifest = manifest          # Scan result / 扫描结果
        self.dependencies = dependencies or []  # Dependency list / 依赖列表
```

**Construction methods / 构造方式：**

```python
# Method 1: Factory (recommended) / 工厂方法（推荐）
reporter = Reporter.from_path('./src')
# Internally calls scan_project() + scan_dependencies()
# 内部自动调用 scan_project() + scan_dependencies()

# Method 2: Manual (for testing) / 手动构造（适合测试）
manifest = scan_project('./src')
deps = scan_dependencies('./src')
reporter = Reporter(manifest=manifest, dependencies=deps)
```

### `from_path(path)` — Factory method / 工厂方法

```python
@classmethod
def from_path(cls, path: Path | str) -> Reporter:
    root = Path(path).resolve()
    manifest = scan_project(root)      # Step 1: scan files / 扫描文件
    deps = scan_dependencies(root)     # Step 2: analyze imports / 分析 import
    return cls(manifest=manifest, dependencies=deps)
```

### `render_manifest()` → str

Delegates to `ProjectManifest.to_markdown()`. / 直接委托给 `ProjectManifest.to_markdown()`。

### `render_stats()` → str

Generates a Markdown statistics table. / 生成 Markdown 统计表格。

**Output example / 输出示例：**
```markdown
## Project Statistics

| Metric | Value |
|--------|-------|
| Total Python files | 5 |
| Total lines of code | 434 |
| Total modules | 5 |
| Avg lines per file | 86.8 |
```

**Edge case / 边界情况：** Returns `'_No statistics available._'` if `manifest.stats` is None.

### `render_dependencies()` → str

Groups dependencies by source module, deduplicates and sorts targets.

按源模块分组依赖，去重并排序目标。

**Internal logic / 内部逻辑：**
```python
# Step 1: Group by source / 按源模块分组
dep_map: dict[str, list[str]] = {}
for dep in self.dependencies:
    dep_map.setdefault(dep.source, []).append(f'{dep.target} ({dep.import_type})')

# Step 2: For each source, deduplicate and sort / 对每个源，去重并排序
for source, targets in sorted(dep_map.items()):
    unique_targets = sorted(set(targets))
    # Render as ### `source` + bullet list
```

**Output example / 输出示例：**
```markdown
## Module Dependencies

### `main`
- argparse (absolute)
- os (absolute)
- reporter (relative)
- scanner (relative)
- shlex (absolute)

### `scanner`
- ast (absolute)
- collections (absolute)
- models (relative)
- pathlib (absolute)
```

### `render_full_report()` → str

Combines all sub-reports into a single document via `ArchReport`.

通过 `ArchReport` 将所有子报告组合为完整文档。

```python
def render_full_report(self) -> str:
    report = ArchReport(
        title='Architecture Report',
        sections=[
            self.render_manifest(),       # Section 1: manifest / 清单
            self.render_stats(),          # Section 2: statistics / 统计
            self.render_dependencies(),   # Section 3: dependencies / 依赖
        ],
    )
    return report.render()
    # ArchReport.render() joins with '\n\n'
    # 用 '\n\n' 拼接所有段落
```

---

## 4.4 `main.py` — CLI & Interactive Shell / 命令行与交互模式（应用层）

**English:** The top-level application layer. Contains CLI argument parsing, command routing, interactive REPL, and Claude AI chat integration. This is the only module that handles user I/O.

**中文：** 顶层应用模块。包含 CLI 参数解析、命令路由、交互式 REPL 和 Claude AI 对话集成。这是唯一处理用户 I/O 的模块。

**Dependencies / 依赖：** `.reporter`, `.scanner`, `argparse`, `os`, `shlex`, `pathlib`, `anthropic` (lazy), `httpx` (lazy), `json` (lazy)

### 4.4.1 CLI Command System / 命令体系

```
code-robin <command> [arguments]
│
├── scan [path]              Scan project, print manifest
│                            扫描项目，打印清单
│
├── arch [path] [-o file]    Generate full architecture report
│                            生成完整架构报告（可输出文件）
│
├── deps [path]              Analyze module dependencies
│                            分析模块依赖
│
├── stats [path]             Print project statistics
│                            打印项目统计
│
└── interactive              Start interactive REPL
                             启动交互式 REPL
```

All `path` arguments default to `.` (current directory). / 所有 `path` 参数默认为 `.`（当前目录）。

### 4.4.2 `build_parser()` — Argument parsing / 参数解析

```python
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='code-robin',
        description='Read your codebase like Robin reads Poneglyphs...',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # scan: positional path, optional
    scan_parser = subparsers.add_parser('scan', ...)
    scan_parser.add_argument('path', nargs='?', default='.')

    # arch: positional path + --output/-o flag
    arch_parser = subparsers.add_parser('arch', ...)
    arch_parser.add_argument('path', nargs='?', default='.')
    arch_parser.add_argument('--output', '-o', help='write report to file')

    # deps, stats: same pattern as scan
    # interactive: no arguments
```

### 4.4.3 Dual Routing System / 双路由系统

The project has two command routing mechanisms for different contexts.

项目有两套命令路由机制，服务于不同场景。

| Function / 函数 | Context / 场景 | Input / 输入 | Features / 特点 |
|--------|------|------|--------|
| `main(argv)` | CLI direct call / CLI 直接调用 | argparse-parsed args | Type-safe, returns exit code / 类型安全，返回退出码 |
| `run_command(cmd)` | Inside REPL / 交互模式内 | Raw string `"scan ./src"` | `shlex.split()` manual parsing, tolerant / 手动解析，宽容处理 |

**`main()` flow / 执行流程：**
```python
def main(argv=None) -> int:
    args = parser.parse_args(argv)
    if args.command == 'interactive': return interactive()

    reporter = Reporter.from_path(args.path)  # Single scan for all commands / 单次扫描

    if args.command == 'scan':  print(reporter.render_manifest()); return 0
    if args.command == 'arch':
        output = reporter.render_full_report()
        if args.output:
            Path(args.output).write_text(output)  # File output / 文件输出
        else:
            print(output)                          # Stdout / 标准输出
        return 0
    # ... deps, stats similar
```

**`run_command()` flow / 执行流程：**
```python
def run_command(cmd: str) -> None:
    parts = shlex.split(cmd)        # "scan ./src" → ["scan", "./src"]
    command = parts[0]
    path = parts[1] if len(parts) > 1 else '.'

    if command == 'scan':
        reporter = Reporter.from_path(path)
        print(reporter.render_manifest())
    # ... similar for arch, deps, stats, help
    else:
        print(f'Unknown command: {command}')
        # Doesn't exit — just prints error and continues REPL
        # 不退出 — 只打印错误，继续 REPL
```

### 4.4.4 Claude AI Integration / AI 集成

**Architecture / 架构：**

```
chat(user_input, history)
│
├── Check environment variables / 检测环境变量
│   │
│   ├── CLAUDE_CODE_USE_BEDROCK == '1' AND AWS_BEARER_TOKEN_BEDROCK is set
│   │   │
│   │   └── _chat_bedrock(history, model, region, token)
│   │       │
│   │       ├── URL: https://bedrock-runtime.{region}.amazonaws.com/model/{model}/invoke
│   │       ├── Method: httpx.post() with JSON body
│   │       ├── Auth: Bearer token in Authorization header
│   │       ├── API version: bedrock-2023-05-31
│   │       ├── Max tokens: 1024
│   │       └── Response: json['content'][0]['text']
│   │
│   └── Otherwise (default) / 否则（默认）
│       │
│       └── _chat_anthropic(history)
│           │
│           ├── Client: anthropic.Anthropic() — reads ANTHROPIC_API_KEY from env
│           ├── Model: claude-sonnet-4-6-20250514
│           ├── Max tokens: 1024
│           └── Response: response.content[0].text
│
├── Success / 成功:
│   ├── Append assistant message to history / 追加 assistant 消息到历史
│   ├── Print reply / 打印回复
│   └── Return updated history / 返回更新后的历史
│
└── Error / 错误:
    ├── Print error message / 打印错误信息
    ├── history.pop() — rollback user message / 回滚用户消息
    └── Return original history / 返回原始历史
```

**System prompt / 系统提示词：**
```
You are Robin, an expert Python code architecture analyst.
Help users understand their codebase structure, dependencies, and design patterns.
Answer concisely.
```

**Conversation history management / 对话历史管理：**

```python
def chat(user_input: str, history: list[dict]) -> list[dict]:
    # Step 1: Optimistically append user message / 乐观追加用户消息
    history.append({'role': 'user', 'content': user_input})

    try:
        reply = _chat_xxx(history)  # Call API / 调用 API
    except Exception as e:
        print(f'Error: {e}')
        history.pop()               # Rollback on failure / 失败时回滚
        return history

    # Step 2: Append assistant reply / 追加 assistant 回复
    history.append({'role': 'assistant', 'content': reply})
    print(reply)
    return history
```

**Why rollback? / 为什么要回滚？**
The Anthropic Messages API requires strict user/assistant alternation. An orphaned user message without an assistant reply would cause the next API call to fail.

Anthropic Messages API 要求 user/assistant 严格交替。如果只有 user 消息没有 assistant 回复，下次 API 调用会报错。

**Lazy imports / 延迟导入：**
`anthropic`, `httpx`, and `json` are imported inside the chat functions, not at module level. This means the CLI commands (scan, arch, deps, stats) work without these packages installed.

`anthropic`、`httpx` 和 `json` 在 chat 函数内部导入，不在模块顶层。这意味着 CLI 命令（scan、arch、deps、stats）不需要安装这些包也能运行。

### 4.4.5 Interactive REPL / 交互式 REPL

```python
def interactive() -> int:
    history: list[dict] = []           # Session-scoped / 会话级（退出即丢失）
    while True:
        line = input('robin> ').strip()
        if line in ('exit', 'quit'):   break
        first_word = line.split()[0]
        if first_word in COMMANDS:     # {'scan', 'arch', 'deps', 'stats', 'help'}
            run_command(line)           # Local execution, no API cost
                                       # 本地执行，不消耗 API
        else:
            history = chat(line, history)  # Send to Claude AI
                                          # 发送给 Claude AI
```

**Routing rule / 路由规则：**
- First word matches `COMMANDS` → local execution / 首个单词匹配 → 本地执行
- Otherwise → send to Claude AI / 否则 → 发送给 Claude AI

**Exit methods / 退出方式：** `exit`, `quit`, `Ctrl+C`, `Ctrl+D` — all handled gracefully / 均优雅处理

**Session characteristics / 会话特性：**
- History is in-memory only, lost on exit / 历史仅在内存中，退出即丢失
- Local commands don't affect chat history / 本地命令不影响对话历史
- Empty lines are skipped / 空行直接跳过

---

## 4.5 `__init__.py` — Public API / 公开接口

```python
"""code-robin — Read your codebase like Robin reads Poneglyphs."""

from .models import ArchReport, Dependency, Module, ProjectManifest, ProjectStats
from .reporter import Reporter
from .scanner import scan_dependencies, scan_project

__all__ = [
    'ArchReport',           # Report container / 报告容器
    'Dependency',           # Import relationship / 导入关系
    'Module',               # Discovered module / 发现的模块
    'ProjectManifest',      # Complete scan result / 完整扫描结果
    'ProjectStats',         # Aggregate statistics / 聚合统计
    'Reporter',             # Report generator / 报告生成器
    'scan_dependencies',    # AST dependency analysis / AST 依赖分析
    'scan_project',         # Filesystem scanner / 文件系统扫描
]
```

**Not exported (internal) / 未导出（内部使用）：** `main`, `build_parser`, `run_command`, `chat`, `interactive`, `_chat_anthropic`, `_chat_bedrock`

---

# 5. Claude AI Integration / AI 集成架构

## Backend Selection / 后端选择

```
                     Environment Variables / 环境变量
                              │
        ┌─────────────────────┼──────────────────────┐
        │                     │                      │
  CLAUDE_CODE_USE_BEDROCK   AWS_BEARER_TOKEN      ANTHROPIC_API_KEY
  == "1" ?                  non-empty ?            (auto-read by SDK)
        │                     │                      │
        └──────┬──────────────┘                      │
               │                                     │
          Both true?                                 │
          ┌────┴────┐                                │
          │         │                                │
         YES       NO ──────────────────────────────→│
          │                                          │
          ▼                                          ▼
   _chat_bedrock()                          _chat_anthropic()
   ├── httpx.post()                         ├── anthropic.Anthropic()
   ├── Bearer token auth                    ├── Auto API key from env
   ├── bedrock-2023-05-31                   ├── claude-sonnet-4-6-20250514
   └── Manual JSON parsing                  └── SDK handles response
```

## Message Format / 消息格式

```json
[
  {"role": "user", "content": "What patterns does this project use?"},
  {"role": "assistant", "content": "This project uses several patterns..."},
  {"role": "user", "content": "Tell me more about the factory pattern"},
  {"role": "assistant", "content": "The Reporter.from_path() is a factory..."}
]
```

Strict user/assistant alternation required by Anthropic API.

Anthropic API 要求 user/assistant 严格交替。

---

# 6. Testing / 测试体系

## Test Suite Overview / 测试套件概览

| Test Class / 测试类 | Tests / 用例数 | Layer / 层级 | Description / 描述 |
|---------------------|---------------|-------------|-------------------|
| `ScannerTests` | 4 | Core Engine | File scan, stats, error handling, dependency analysis |
| `ReporterTests` | 3 | Aggregation | Full report, manifest rendering, stats rendering |
| `ModelTests` | 2 | Data Models | Module creation, manifest Markdown output |
| `CLITests` | 3 | Application | End-to-end CLI commands (scan, arch, stats) |
| **Total** | **12** | | |

## Test Details / 测试详情

### ScannerTests (4 tests / 测试)

```python
test_scan_finds_python_files
# Verifies: scan_project() finds >= 4 Python files and modules list is non-empty
# 验证：scan_project() 找到 >= 4 个 Python 文件，且模块列表非空

test_scan_includes_stats
# Verifies: manifest.stats is not None, total_lines > 0, avg_lines_per_file > 0
# 验证：统计信息存在，总行数 > 0，平均行数 > 0

test_scan_nonexistent_dir_raises
# Verifies: ValueError raised for non-existent directory
# 验证：不存在的目录抛出 ValueError

test_scan_dependencies_returns_list
# Verifies: scan_dependencies() returns non-empty list
# 验证：scan_dependencies() 返回非空列表
```

### ReporterTests (3 tests / 测试)

```python
test_full_report_contains_sections
# Verifies: render_full_report() includes all 3 section headers
# 验证：完整报告包含全部 3 个段落标题

test_manifest_markdown
# Verifies: render_manifest() contains "Total Python files" and "Modules:"
# 验证：清单渲染包含关键文本

test_stats_markdown
# Verifies: render_stats() contains "Total Python files" and "Total lines of code"
# 验证：统计渲染包含关键文本
```

### ModelTests (2 tests / 测试)

```python
test_module_creation
# Verifies: Module dataclass fields are correctly stored
# 验证：Module 数据类字段正确存储

test_manifest_to_markdown
# Verifies: ProjectManifest.to_markdown() renders correct Markdown with stats
# 验证：to_markdown() 渲染正确的 Markdown（含统计信息）
```

### CLITests (3 tests / 测试)

```python
test_cli_scan_runs
# Verifies: `python3 -m src.main scan ./src` succeeds and outputs "Project Manifest"
# 验证：CLI scan 命令成功执行并输出 "Project Manifest"

test_cli_arch_runs
# Verifies: `python3 -m src.main arch ./src` succeeds and outputs "Architecture Report"
# 验证：CLI arch 命令成功执行并输出 "Architecture Report"

test_cli_stats_runs
# Verifies: `python3 -m src.main stats ./src` succeeds and outputs stats
# 验证：CLI stats 命令成功执行并输出统计信息
```

## Test Coverage Hierarchy / 测试覆盖层级

```
CLITests (integration / 集成)
  └── main() → Reporter → scanner → models

ReporterTests (aggregation / 聚合)
  └── Reporter → scanner → models

ScannerTests (core / 核心)
  └── scanner → models

ModelTests (unit / 单元)
  └── models (isolated / 独立)
```

**Not covered / 未覆盖：** Interactive REPL, Claude AI chat (requires API key and network).

**未覆盖：** 交互式 REPL、Claude AI 对话（需要 API 密钥和网络）。

## Running Tests / 运行测试

```bash
python3 -m unittest discover -s tests -v

# Expected output / 预期输出:
# test_cli_arch_runs ... ok
# test_cli_scan_runs ... ok
# test_cli_stats_runs ... ok
# test_manifest_to_markdown ... ok
# test_module_creation ... ok
# test_full_report_contains_sections ... ok
# test_manifest_markdown ... ok
# test_stats_markdown ... ok
# test_scan_dependencies_returns_list ... ok
# test_scan_finds_python_files ... ok
# test_scan_includes_stats ... ok
# test_scan_nonexistent_dir_raises ... ok
# -----------------------------------------------
# Ran 12 tests in 0.XXXs
# OK
```

---

# 7. Configuration / 配置说明

## pyproject.toml

```toml
[project]
name = "code-robin"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "anthropic>=0.80.0",    # Claude AI SDK
    "httpx>=0.27.0",        # HTTP client for Bedrock
]

[project.optional-dependencies]
bedrock = ["boto3>=1.35.0"]  # AWS Bedrock support
dev = ["pytest>=8.0"]        # Development tools

[project.scripts]
code-robin = "src.main:main"  # CLI entry point
```

## Environment Variables / 环境变量

| Variable / 变量 | Required / 必需 | Description / 描述 | Default / 默认值 |
|---------|---------|-------------|---------|
| `ANTHROPIC_API_KEY` | For AI chat / AI 对话时 | Anthropic API key / API 密钥 | — |
| `CLAUDE_CODE_USE_BEDROCK` | No | Set to `1` to use Bedrock / 设为 `1` 启用 Bedrock | disabled |
| `AWS_BEARER_TOKEN_BEDROCK` | For Bedrock | AWS auth token / AWS 认证令牌 | — |
| `AWS_REGION` | No | AWS region / AWS 区域 | `us-east-1` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | No | Bedrock model ID / 模型 ID | `us.anthropic.claude-sonnet-4-6` |

**Note / 注意：** Scanning commands (scan, arch, deps, stats) work without any API keys. Only the interactive chat feature requires them.

扫描命令（scan、arch、deps、stats）不需要任何 API 密钥。只有交互式对话功能需要。

---

# 8. Extension Guide / 扩展指南

## Add a new CLI command / 新增 CLI 命令

Example: adding a `tree` command / 以新增 `tree` 命令为例：

```python
# Step 1: Register parser / 注册解析器 (main.py:build_parser)
tree_parser = subparsers.add_parser('tree', help='print directory tree')
tree_parser.add_argument('path', nargs='?', default='.')

# Step 2: Add to main() / 在 main() 中添加
if args.command == 'tree':
    # Implementation / 实现逻辑
    return 0

# Step 3: Add to COMMANDS set / 添加到 COMMANDS 集合
COMMANDS = {'scan', 'arch', 'deps', 'stats', 'help', 'tree'}

# Step 4: Add to run_command() / 在 run_command() 中添加
elif command == 'tree':
    # Implementation / 实现逻辑
```

## Add a new report section / 新增报告段落

```python
# Step 1: Add render method to Reporter / 在 Reporter 中添加渲染方法
def render_complexity(self) -> str:
    """Render cyclomatic complexity analysis."""
    # ...

# Step 2: Include in render_full_report() / 加入完整报告
sections=[
    self.render_manifest(),
    self.render_stats(),
    self.render_dependencies(),
    self.render_complexity(),       # New section / 新段落
],
```

## Add a new data model / 新增数据模型

```python
# Step 1: Define in models.py / 在 models.py 中定义
@dataclass(frozen=True)
class FunctionInfo:
    name: str
    module: str
    line_count: int
    complexity: int

# Step 2: Export in __init__.py / 在 __init__.py 中导出
from .models import FunctionInfo
__all__ = [..., 'FunctionInfo']
```

## Add a new AI backend / 新增 AI 后端

```python
# Step 1: Add _chat_xxx() function in main.py / 在 main.py 中添加
def _chat_openai(messages: list[dict]) -> str:
    import openai
    # ...

# Step 2: Add branch in chat() / 在 chat() 中添加分支
if os.environ.get('USE_OPENAI') == '1':
    reply = _chat_openai(history)
```

---

# 9. Design Decisions / 设计决策

## Why dataclasses instead of Pydantic? / 为什么用 dataclasses 而不是 Pydantic？

**English:** All models are simple value containers without validation needs. `dataclasses` is stdlib, adding zero dependencies. Pydantic would be overkill for this scale.

**中文：** 所有模型都是简单的值容器，不需要验证。`dataclasses` 是标准库，零额外依赖。对这个规模的项目来说 Pydantic 过于重量级。

## Why `frozen=True` for Module, Dependency, ProjectStats? / 为什么这些类用 frozen？

**English:** These are value objects — once created, they shouldn't change. Immutability makes them safe to pass around, store in tuples, and use as dict keys.

**中文：** 这些是值对象 — 创建后不应改变。不可变性使它们可以安全传递、存入 tuple、用作 dict key。

## Why two routing systems? / 为什么有两套路由？

**English:** `main()` uses argparse for strict validation and exit codes — needed for CI/scripting. `run_command()` uses lenient string parsing — needed for REPL where unknown commands shouldn't crash the session.

**中文：** `main()` 用 argparse 做严格校验和退出码 — CI/脚本场景需要。`run_command()` 用宽容的字符串解析 — REPL 场景中未知命令不应该崩溃会话。

## Why lazy imports for AI packages? / 为什么 AI 包延迟导入？

**English:** `anthropic` and `httpx` are only needed for the chat feature. Lazy importing means `scan`, `arch`, `deps`, and `stats` commands work even without these packages installed. This is important for CI environments where only scanning is needed.

**中文：** `anthropic` 和 `httpx` 只有对话功能需要。延迟导入意味着 `scan`、`arch`、`deps`、`stats` 命令即使不安装这些包也能运行。这对只需要扫描功能的 CI 环境很重要。

## Why linear dependency chain? / 为什么采用线性依赖链？

**English:** `main → reporter → scanner → models` — each layer only knows about the one below it. This makes testing easy (mock one layer), changes localized (modify scanner without touching main), and the mental model simple.

**中文：** `main → reporter → scanner → models` — 每层只知道下一层。这使测试简单（mock 一层即可）、变更局部化（修改 scanner 不影响 main）、心智模型清晰。

## Why Counter instead of manual dict? / 为什么用 Counter 而不是手动 dict？

**English:** `Counter` provides `most_common()` for free, sorting modules by file count descending. It's stdlib, well-tested, and more readable than manual counting logic.

**中文：** `Counter` 免费提供 `most_common()`，按文件数降序排列模块。是标准库，经过充分测试，比手动计数逻辑更可读。

---

*Generated by code-robin. Read your codebase like Robin reads Poneglyphs.*

*由 code-robin 生成。像 Robin 阅读历史正文一样阅读你的代码。*

---

## Author / 作者

![](https://fisherai-1312281807.cos.ap-guangzhou.myqcloud.com/6df7dfc5e5e5ea9267ed62795a992e4d.bmp)
