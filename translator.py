import os
import re
import logging

import httpx

_cache: dict[str, str] = {}

_PROTECTED_NAMES = [
    "Claude Code Review",
    "Claude Code on the web",
    "Claude Code",
    "Claude Cowork",
    "Cowork Remote",
    "Claude Tag",
    "Claude",
    "Opus",
    "Sonnet",
    "Haiku",
    "Mythos",
    "Fable",
]
# nomes compostos precisam ser testados antes dos nomes simples que os compõem
_PROTECTED_NAMES.sort(key=len, reverse=True)

OPENROUTER_DEFAULT = "meta-llama/llama-3.1-8b-instruct"
OLLAMA_DEFAULT_MODEL = "gemma4:12b"
# a primeira chamada carrega o modelo na GPU, o que pode levar mais de um minuto
OLLAMA_DEFAULT_TIMEOUT = 240
OLLAMA_DEFAULT_ENDPOINT = "http://localhost:11434"
# libera a GPU logo depois da tradução
OLLAMA_DEFAULT_KEEP_ALIVE = "1m"
MAX_TOKENS = 1024


def _cfg() -> tuple[str, str]:
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

    # protege nomes de modelos contra tradução
    protected = {}
    def _protect(m: re.Match) -> str:
        placeholder = f"\x00PROTECTED_{len(protected)}\x00"
        protected[placeholder] = m.group(0)
        return placeholder
    text_protected = re.sub(
        r"\b(?:" + "|".join(re.escape(n) for n in _PROTECTED_NAMES) + r")\b",
        _protect,
        text,
    )

    prompt = (
        f"Translate the following text to {target}. "
        f"Return ONLY the translation, nothing else.\n\nText: {text_protected}"
    )

    try:
        result = await _call_llm(prompt, provider)
        for placeholder, original in protected.items():
            result = result.replace(placeholder, original)
        _cache[cache_key] = result
        return result
    except Exception as e:
        logging.error(
            "Falha na tradução (%s), mensagem enviada no original: %s",
            provider,
            e or type(e).__name__,
        )
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
                "max_tokens": MAX_TOKENS,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _call_ollama(prompt: str) -> str:
    endpoint = os.environ.get("OLLAMA_ENDPOINT", "") or OLLAMA_DEFAULT_ENDPOINT
    model = os.environ.get("OLLAMA_MODEL", "") or OLLAMA_DEFAULT_MODEL
    timeout = float(os.environ.get("OLLAMA_TIMEOUT_SECONDS", "") or OLLAMA_DEFAULT_TIMEOUT)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{endpoint.rstrip('/')}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": os.environ.get("OLLAMA_KEEP_ALIVE", "") or OLLAMA_DEFAULT_KEEP_ALIVE,
                "options": {"temperature": 0, "num_predict": MAX_TOKENS},
            },
            timeout=timeout,
        )
        if resp.status_code >= 400:
            raise RuntimeError(f"Ollama {resp.status_code} com {model}: {resp.text[:200]}")
        result = resp.json().get("response", "").strip()
        if not result:
            raise RuntimeError(f"Ollama devolveu resposta vazia com {model}")
        return result
