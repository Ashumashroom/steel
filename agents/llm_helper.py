"""
LLM helper — unified interface for HuggingFace / Ollama / Groq inference.
"""
import os, json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    INFERENCE_MODE, HF_API_TOKEN, HF_PRIMARY_MODEL, HF_ROUTER_MODEL,
    HF_INFERENCE_URL, GROQ_API_KEY, GROQ_PRIMARY_MODEL, GROQ_ROUTER_MODEL,
    OLLAMA_BASE_URL, OLLAMA_PRIMARY_MODEL, OLLAMA_ROUTER_MODEL,
    AGENT_TEMPERATURE, AGENT_MAX_TOKENS,
)
from utils.logger import get_logger

log = get_logger("agents.llm")


def call_llm(prompt: str, system_prompt: str = "", use_router_model: bool = False) -> str:
    """Call LLM with the configured inference backend."""
    mode = INFERENCE_MODE.lower()
    if mode == "groq":
        return _call_groq(prompt, system_prompt, use_router_model)
    elif mode == "ollama":
        return _call_ollama(prompt, system_prompt, use_router_model)
    else:
        return _call_huggingface(prompt, system_prompt, use_router_model)


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
    client = Groq(api_key=GROQ_API_KEY)

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
