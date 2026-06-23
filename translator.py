import os
import logging

import httpx

_cache: dict[str, str] = {}

OPENROUTER_DEFAULT = "meta-llama/llama-3.1-8b-instruct"
OLLAMA_DEFAULT_MODEL = "gemma3:4b"
OLLAMA_DEFAULT_ENDPOINT = "http://localhost:11434"


def _cfg() -> tuple[str, str, str]:
    provider = os.environ.get("LLM_PROVIDER", "")
    target = os.environ.get("TRANSLATE_TO", "")
    return provider, target


async def translate(text: str) -> str:
    provider, target = _cfg()
    if not provider or not target:
        return text

    cache_key = f"{provider}:{target}:{text}"
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    prompt = (
        f"Translate the following text to {target}. "
        f"Return ONLY the translation, nothing else.\n\nText: {text}"
    )

    try:
        result = await _call_llm(prompt, provider)
        _cache[cache_key] = result
        return result
    except Exception as e:
        logging.warning("Falha na tradução: %s", e)
        return text


async def _call_llm(prompt: str, provider: str) -> str:
    if provider == "openrouter":
        return await _call_openrouter(prompt)
    if provider == "ollama":
        return await _call_ollama(prompt)
    raise ValueError(f"LLM_PROVIDER desconhecido: {provider}")


async def _call_openrouter(prompt: str) -> str:
    key = os.environ.get("OPENROUTER_KEY", "")
    if not key:
        raise RuntimeError("OPENROUTER_KEY não configurada")
    model = os.environ.get("OPENROUTER_MODEL", "") or OPENROUTER_DEFAULT

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
                "max_tokens": 200,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _call_ollama(prompt: str) -> str:
    endpoint = os.environ.get("OLLAMA_ENDPOINT", "") or OLLAMA_DEFAULT_ENDPOINT
    model = os.environ.get("OLLAMA_MODEL", "") or OLLAMA_DEFAULT_MODEL

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{endpoint.rstrip('/')}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0, "num_predict": 200},
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()
