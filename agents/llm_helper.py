"""
LLM helper — unified interface for HuggingFace / Ollama / Groq / Gemini inference.
"""
import os, json, hashlib, time
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config
from config import (
    INFERENCE_MODE, HF_API_TOKEN, HF_PRIMARY_MODEL, HF_ROUTER_MODEL,
    HF_INFERENCE_URL, GROQ_API_KEY, GROQ_PRIMARY_MODEL, GROQ_ROUTER_MODEL,
    OLLAMA_BASE_URL, OLLAMA_PRIMARY_MODEL, OLLAMA_ROUTER_MODEL,
    GEMINI_PRIMARY_MODEL, GEMINI_ROUTER_MODEL,
    AGENT_TEMPERATURE, AGENT_MAX_TOKENS,
)
from utils.logger import get_logger

log = get_logger("agents.llm")


# ──────────────────────────────────────────────
# Simple in-memory response cache
# ──────────────────────────────────────────────
_LLM_CACHE: dict[str, tuple[float, str]] = {}
_LLM_CACHE_TTL = 300  # seconds
_LLM_CACHE_MAX = 200


def _cache_key(prompt: str, system_prompt: str, model: str) -> str:
    raw = f"{model}|{system_prompt}|{prompt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_get(key: str) -> str | None:
    entry = _LLM_CACHE.get(key)
    if not entry:
        return None
    ts, value = entry
    if time.time() - ts > _LLM_CACHE_TTL:
        _LLM_CACHE.pop(key, None)
        return None
    return value


def _cache_set(key: str, value: str):
    if len(_LLM_CACHE) >= _LLM_CACHE_MAX:
        oldest_key = min(_LLM_CACHE, key=lambda k: _LLM_CACHE[k][0])
        _LLM_CACHE.pop(oldest_key, None)
    _LLM_CACHE[key] = (time.time(), value)


def call_llm(prompt: str, system_prompt: str = "", use_router_model: bool = False) -> str:
    """Call LLM with the configured inference backend."""
    mode = config.INFERENCE_MODE.lower()
    if mode == "gemini":
        return _call_gemini(prompt, system_prompt, use_router_model)
    elif mode == "groq":
        return _call_groq(prompt, system_prompt, use_router_model)
    elif mode == "ollama":
        return _call_ollama(prompt, system_prompt, use_router_model)
    else:
        return _call_huggingface(prompt, system_prompt, use_router_model)


# ──────────────────────────────────────────────
# Reusable Gemini client (rebuilt only if the API key changes)
# ──────────────────────────────────────────────
_gemini_client = None
_gemini_client_key = None


def _get_gemini_client(api_key: str):
    global _gemini_client, _gemini_client_key
    from google import genai
    if _gemini_client is None or _gemini_client_key != api_key:
        _gemini_client = genai.Client(api_key=api_key)
        _gemini_client_key = api_key
    return _gemini_client


def _call_gemini(prompt: str, system_prompt: str, use_router: bool) -> str:
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return "[Error: google-genai package not installed. Run: pip install google-genai]"

    # Read dynamically so a runtime sidebar override (config.GEMINI_API_KEY)
    # is respected without restarting the app.
    api_key = config.GEMINI_API_KEY
    if not api_key:
        return "[Error: GEMINI_API_KEY not set. Add it in the sidebar or .env file]"

    model = GEMINI_ROUTER_MODEL if use_router else GEMINI_PRIMARY_MODEL

    cache_key = _cache_key(prompt, system_prompt, model)
    cached = _cache_get(cache_key)
    if cached is not None:
        log.info(f"LLM cache hit ({model})")
        return cached

    try:
        client = _get_gemini_client(api_key)
        config_kwargs = {
            "temperature": AGENT_TEMPERATURE,
            "max_output_tokens": AGENT_MAX_TOKENS,
        }
        if system_prompt:
            config_kwargs["system_instruction"] = system_prompt

        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        result = (response.text or "").strip()
        if result and not result.startswith("[LLM Error"):
            _cache_set(cache_key, result)
        return result
    except Exception as e:
        log.error(f"Gemini API error: {e}")
        return f"[LLM Error: {e}]"


def _call_huggingface(prompt: str, system_prompt: str, use_router: bool) -> str:
    import requests
    model = HF_ROUTER_MODEL if use_router else HF_PRIMARY_MODEL
    url = f"{HF_INFERENCE_URL}{model}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    # Build chat messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "inputs": prompt if not system_prompt else f"{system_prompt}\n\nUser: {prompt}",
        "parameters": {
            "temperature": AGENT_TEMPERATURE,
            "max_new_tokens": AGENT_MAX_TOKENS,
            "return_full_text": False,
        },
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "").strip()
        return str(result)
    except Exception as e:
        log.error(f"HuggingFace API error: {e}")
        return f"[LLM Error: {e}]"


def _call_groq(prompt: str, system_prompt: str, use_router: bool) -> str:
    try:
        from groq import Groq
    except ImportError:
        return "[Error: groq package not installed. Run: pip install groq]"

    model = GROQ_ROUTER_MODEL if use_router else GROQ_PRIMARY_MODEL
    client = Groq(api_key=config.GROQ_API_KEY)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=model, messages=messages,
            temperature=AGENT_TEMPERATURE, max_tokens=AGENT_MAX_TOKENS,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        log.error(f"Groq API error: {e}")
        return f"[LLM Error: {e}]"


def _call_ollama(prompt: str, system_prompt: str, use_router: bool) -> str:
    import requests
    model = OLLAMA_ROUTER_MODEL if use_router else OLLAMA_PRIMARY_MODEL
    url = f"{OLLAMA_BASE_URL}/api/generate"

    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    payload = {
        "model": model, "prompt": full_prompt, "stream": False,
        "options": {"temperature": AGENT_TEMPERATURE, "num_predict": AGENT_MAX_TOKENS},
    }
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        log.error(f"Ollama error: {e}")
        return f"[LLM Error: {e}]"