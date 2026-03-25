"""Unified LLM interface – supports Anthropic Claude, OpenAI GPT, and Bifrost proxy models."""

from __future__ import annotations
import json
import streamlit as st


def _get_locale_suffix() -> str:
    """Build localisation suffix from session state."""
    locale = st.session_state.get("locale_config")
    if not locale:
        return ""
    return f"\n\nLOCALISATION: {locale.get('spelling_notes', '')}"


def call_llm(
    system_prompt: str,
    user_prompt: str,
    provider: str = "anthropic",
    model: str = "",
    api_key: str = "",
    response_format: str = "text",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    inject_locale: bool = True,
) -> str:
    """Call LLM and return text response.

    Args:
        response_format: "text" or "json". For json, instructs LLM to return valid JSON.
        inject_locale: If True, appends locale spelling notes to system prompt.
    """
    if inject_locale:
        system_prompt += _get_locale_suffix()

    if response_format == "json":
        system_prompt += "\n\nYou MUST respond with valid JSON only. No markdown code fences, no extra text."

    if provider == "anthropic":
        return _call_anthropic(system_prompt, user_prompt, model, api_key, temperature, max_tokens)
    elif provider == "openai":
        return _call_openai(system_prompt, user_prompt, model, api_key, temperature, max_tokens, response_format)
    elif provider == "bifrost":
        return _call_bifrost(system_prompt, user_prompt, model, api_key, temperature, max_tokens, response_format)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _call_anthropic(
    system_prompt: str,
    user_prompt: str,
    model: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
) -> str:
    import anthropic

    model = model or "claude-sonnet-4-20250514"
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def _call_openai(
    system_prompt: str,
    user_prompt: str,
    model: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    response_format: str,
) -> str:
    from openai import OpenAI

    model = model or "gpt-4o"
    client = OpenAI(api_key=api_key)

    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}

    completion = client.chat.completions.create(**kwargs)
    return completion.choices[0].message.content


BIFROST_BASE_URL = "https://bifrost.pattern.com/v1"

BIFROST_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    "openai/o3-mini",
    "anthropic/claude-sonnet-4-20250514",
    "anthropic/claude-haiku-4-20250514",
    "deepseek/deepseek-chat",
    "mistral/mistral-large-latest",
    "groq/llama-3.1-70b-versatile",
    "together_ai/meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    "fireworks_ai/accounts/fireworks/models/llama-v3p1-70b-instruct",
]


def _call_bifrost(
    system_prompt: str,
    user_prompt: str,
    model: str,
    api_key: str,
    temperature: float,
    max_tokens: int,
    response_format: str,
) -> str:
    from openai import OpenAI

    model = model or "openai/gpt-4o"
    client = OpenAI(base_url=BIFROST_BASE_URL, api_key=api_key)

    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}

    completion = client.chat.completions.create(**kwargs)
    return completion.choices[0].message.content


def parse_llm_json(text: str) -> dict | None:
    """Try to parse JSON from LLM response, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (fences)
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
