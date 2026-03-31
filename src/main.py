from __future__ import annotations

import argparse
import os
import shlex
from pathlib import Path

from .config import configure_interactive, get_default_provider_name, load_env
from .providers import PROVIDER_MAP, PROVIDERS, chat_completion, detect_provider, get_provider
from .reporter import Reporter

COMMANDS = {'scan', 'arch', 'deps', 'stats', 'help', 'model', 'models'}

HELP_TEXT = """Available commands:
  scan [path]              scan a Python project and print manifest
  arch [path]              generate full architecture report
  deps [path]              analyze and print module dependencies
  stats [path]             print project statistics
  model [provider] [model] switch provider and/or model
                           e.g. model openrouter google/gemini-2.0-flash
  models                   list all available providers and status
  help                     show this help message
  exit / quit              exit the interactive shell

Any other input will be sent to the current LLM as a conversation.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='code-robin',
        description='Read your codebase like Robin reads Poneglyphs — Python project architecture analyzer',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    scan_parser = subparsers.add_parser('scan', help='scan a Python project and print manifest')
    scan_parser.add_argument('path', nargs='?', default='.', help='project root path (default: current directory)')

    arch_parser = subparsers.add_parser('arch', help='generate full architecture report')
    arch_parser.add_argument('path', nargs='?', default='.', help='project root path')
    arch_parser.add_argument('--output', '-o', help='write report to file instead of stdout')

    deps_parser = subparsers.add_parser('deps', help='analyze module dependencies')
    deps_parser.add_argument('path', nargs='?', default='.', help='project root path')

    stats_parser = subparsers.add_parser('stats', help='print project statistics')
    stats_parser.add_argument('path', nargs='?', default='.', help='project root path')

    interactive_parser = subparsers.add_parser('interactive', help='start an interactive shell')
    interactive_parser.add_argument('--provider', '-p', help='provider name (e.g. deepseek, openrouter)')
    interactive_parser.add_argument('--model', '-m', help='model ID (e.g. google/gemini-2.0-flash)')
    interactive_parser.add_argument('--key', '-k', help='API key (overrides env/config)')

    subparsers.add_parser('configure', help='configure API keys for LLM providers')

    subparsers.add_parser('models', help='list all supported providers')

    return parser


def _resolve_path(path_str: str) -> Path:
    return Path(path_str).resolve()


def run_command(cmd: str, state: dict) -> None:
    """Execute a command in interactive mode."""
    parts = shlex.split(cmd)
    command = parts[0]

    if command == 'model':
        if len(parts) < 2:
            p = state.get('provider')
            model_id = state.get('model_id', p.default_model if p else '?')
            print(f'Current: {p.label_zh} ({p.name}, model={model_id})' if p else 'No provider set.')
            return
        try:
            state['provider'] = get_provider(parts[1])
            if len(parts) >= 3:
                state['model_id'] = parts[2]
            else:
                state['model_id'] = state['provider'].default_model
            p = state['provider']
            print(f'Switched to {p.label_zh} ({p.name}, model: {state["model_id"]})')
        except ValueError as e:
            print(e)
        return

    if command == 'models':
        print_providers()
        return

    path = _resolve_path(parts[1]) if len(parts) > 1 else _resolve_path('.')
    if command == 'scan':
        reporter = Reporter.from_path(path)
        print(reporter.render_manifest())
    elif command == 'arch':
        reporter = Reporter.from_path(path)
        print(reporter.render_full_report())
    elif command == 'deps':
        reporter = Reporter.from_path(path)
        print(reporter.render_dependencies())
    elif command == 'stats':
        reporter = Reporter.from_path(path)
        print(reporter.render_stats())
    elif command == 'help':
        print(HELP_TEXT)
    else:
        print(f'Unknown command: {command}')
        print('Type "help" for available commands.')


def print_providers() -> None:
    """List all supported providers and their key status."""
    print('\n  Available providers:\n')
    for p in PROVIDERS:
        has_key = bool(os.environ.get(p.env_key))
        status = '\033[32m✓\033[0m' if has_key else '\033[90m✗\033[0m'
        print(f'  {status}  {p.name:<12} {p.label_zh:<24} model: {p.default_model}')
    print(f'\n  Run `code-robin configure` to add API keys.')
    print(f'  Use `model <name>` in interactive mode to switch.\n')


def chat(user_input: str, history: list[dict], provider, model_id: str | None = None) -> list[dict]:
    """Send user input to the current provider."""
    history.append({'role': 'user', 'content': user_input})
    try:
        reply = chat_completion(history, provider, model=model_id)
    except Exception as e:
        print(f'Error: {e}')
        history.pop()
        return history
    history.append({'role': 'assistant', 'content': reply})
    print(reply)
    return history


def interactive(provider_name: str | None = None, model_id: str | None = None, api_key: str | None = None) -> int:
    """Run the interactive REPL."""
    # Load .env config
    load_env()

    # Resolve provider
    provider = None
    if provider_name:
        try:
            provider = get_provider(provider_name)
        except ValueError as e:
            print(f'Error: {e}')
            return 1
    if not provider:
        default_name = get_default_provider_name()
        if default_name:
            provider = PROVIDER_MAP.get(default_name)
    if not provider:
        provider = detect_provider()
    if not provider:
        if not api_key:
            print('No API key configured. Run `code-robin configure` first,')
            print('or pass --provider and --key directly.')
            return 1
        # Default to openrouter if key provided without provider
        provider = get_provider('openrouter')

    # --key overrides env for the selected provider
    if api_key:
        os.environ[provider.env_key] = api_key

    model_id = model_id or provider.default_model

    print('code-robin — Interactive Mode')
    print('Read your codebase like Robin reads Poneglyphs.')
    print(f'Current: {provider.label_zh} ({provider.name}, model: {model_id})')
    print('Type "help" for commands, "models" to list providers, "exit" to quit.\n')

    state = {'provider': provider, 'model_id': model_id}
    history: list[dict] = []

    while True:
        try:
            line = input('robin> ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line in ('exit', 'quit'):
            break
        first_word = line.split()[0]
        if first_word in COMMANDS:
            run_command(line, state)
        else:
            history = chat(line, history, state['provider'], state.get('model_id'))
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == 'configure':
        configure_interactive()
        return 0

    if args.command == 'models':
        load_env()
        print_providers()
        return 0

    if args.command == 'interactive':
        return interactive(
            getattr(args, 'provider', None),
            getattr(args, 'model', None),
            getattr(args, 'key', None),
        )

    path = _resolve_path(getattr(args, 'path', '.'))
    reporter = Reporter.from_path(path)

    if args.command == 'scan':
        print(reporter.render_manifest())
        return 0

    if args.command == 'arch':
        output = reporter.render_full_report()
        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f'Report written to {args.output}')
        else:
            print(output)
        return 0

    if args.command == 'deps':
        print(reporter.render_dependencies())
        return 0

    if args.command == 'stats':
        print(reporter.render_stats())
        return 0

    parser.error(f'unknown command: {args.command}')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
