"""Unified multi-provider LLM abstraction.

Most Chinese and international providers support the OpenAI-compatible API,
so we use the openai package with different base_url for most providers.
Anthropic uses its native SDK.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    """Configuration for a single LLM provider."""
    name: str            # display name
    env_key: str         # environment variable for the API key
    base_url: str        # OpenAI-compatible base URL (empty for Anthropic native)
    default_model: str   # default model ID
    label_zh: str        # Chinese label for interactive prompts


# Registry of all supported providers, ordered for the configure menu.
PROVIDERS: tuple[ProviderConfig, ...] = (
    # --- International ---
    ProviderConfig('anthropic', 'ANTHROPIC_API_KEY', '', 'claude-sonnet-4-6-20250514', 'Anthropic (Claude)'),
    ProviderConfig('openai', 'OPENAI_API_KEY', 'https://api.openai.com/v1', 'gpt-4o', 'OpenAI (GPT)'),
    ProviderConfig('google', 'GOOGLE_API_KEY', 'https://generativelanguage.googleapis.com/v1beta/openai', 'gemini-2.0-flash', 'Google (Gemini)'),
    ProviderConfig('groq', 'GROQ_API_KEY', 'https://api.groq.com/openai/v1', 'llama-3.3-70b-versatile', 'Groq'),
    ProviderConfig('openrouter', 'OPENROUTER_API_KEY', 'https://openrouter.ai/api/v1', 'anthropic/claude-sonnet-4', 'OpenRouter (多模型聚合)'),
    # --- China ---
    ProviderConfig('deepseek', 'DEEPSEEK_API_KEY', 'https://api.deepseek.com/v1', 'deepseek-chat', 'DeepSeek (深度求索)'),
    ProviderConfig('zhipu', 'ZHIPU_API_KEY', 'https://open.bigmodel.cn/api/paas/v4', 'glm-4-flash', '智谱 AI (GLM)'),
    ProviderConfig('qwen', 'DASHSCOPE_API_KEY', 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-plus', '通义千问 (Qwen/百炼)'),
    ProviderConfig('moonshot', 'MOONSHOT_API_KEY', 'https://api.moonshot.cn/v1', 'moonshot-v1-8k', '月之暗面 (Kimi)'),
    ProviderConfig('baichuan', 'BAICHUAN_API_KEY', 'https://api.baichuan-ai.com/v1', 'Baichuan4-Air', '百川智能'),
    ProviderConfig('minimax', 'MINIMAX_API_KEY', 'https://api.minimax.chat/v1', 'MiniMax-Text-01', 'MiniMax (稀宇)'),
    ProviderConfig('yi', 'YI_API_KEY', 'https://api.lingyiwanwu.com/v1', 'yi-lightning', '零一万物 (Yi)'),
    ProviderConfig('siliconflow', 'SILICONFLOW_API_KEY', 'https://api.siliconflow.cn/v1', 'deepseek-ai/DeepSeek-V3', '硅基流动 (SiliconFlow)'),
    ProviderConfig('stepfun', 'STEPFUN_API_KEY', 'https://api.stepfun.com/v1', 'step-2-16k', '阶跃星辰 (StepFun)'),
    ProviderConfig('spark', 'SPARK_API_KEY', 'https://spark-api-open.xf-yun.com/v1', 'generalv3.5', '讯飞星火 (Spark)'),
)

PROVIDER_MAP: dict[str, ProviderConfig] = {p.name: p for p in PROVIDERS}

SYSTEM_PROMPT = (
    'You are Robin, an expert Python code architecture analyst. '
    'Help users understand their codebase structure, dependencies, and design patterns. '
    'Answer concisely.'
)


def get_provider(name: str) -> ProviderConfig:
    """Look up a provider by name."""
    if name not in PROVIDER_MAP:
        available = ', '.join(PROVIDER_MAP)
        raise ValueError(f'Unknown provider: {name}. Available: {available}')
    return PROVIDER_MAP[name]


def detect_provider() -> ProviderConfig | None:
    """Auto-detect the first provider that has an API key set in the environment."""
    for p in PROVIDERS:
        if os.environ.get(p.env_key):
            return p
    return None


def chat_completion(messages: list[dict], provider: ProviderConfig, model: str | None = None) -> str:
    """Send messages to the specified provider and return the assistant reply."""
    model = model or provider.default_model
    api_key = os.environ.get(provider.env_key, '')
    if not api_key:
        raise RuntimeError(
            f'API key not set for {provider.label_zh}. '
            f'Run `code-robin configure` or set {provider.env_key}.'
        )

    if provider.name == 'anthropic':
        return _chat_anthropic(messages, model, api_key)
    return _chat_openai_compat(messages, model, api_key, provider.base_url)


def _chat_anthropic(messages: list[dict], model: str, api_key: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def _chat_openai_compat(messages: list[dict], model: str, api_key: str, base_url: str) -> str:
    import httpx
    import json

    payload = {
        'model': model,
        'max_tokens': 1024,
        'messages': [{'role': 'system', 'content': SYSTEM_PROMPT}, *messages],
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    url = f'{base_url.rstrip("/")}/chat/completions'
    resp = httpx.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    data = json.loads(resp.text)
    return data['choices'][0]['message']['content']
