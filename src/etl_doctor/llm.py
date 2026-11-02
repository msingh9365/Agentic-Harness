"""One place that knows how to talk to the LLM provider.

NVIDIA's API (build.nvidia.com) speaks the OpenAI Chat Completions protocol, so we reuse
PydanticAI's OpenAI model class and only swap the base URL and key. Switching provider
later (Azure, OpenAI, a local vLLM) means changing this file, not the agents.
"""

import os

from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# Chosen from the smoke test in scripts/smoke_llm.py (results: docs/04-model-smoke-test.md).
# The free tier changes under you: on 2026-11-02 Nemotron 3 Super (the October default)
# returned 404 and gpt-oss-20b took ~150 s per call, while Ultra, overloaded in October,
# answered in seconds. Re-run `make smoke` before a demo. Override with these env vars.
STRONG_MODEL = os.environ.get("ETLDOC_STRONG_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
FAST_MODEL = os.environ.get("ETLDOC_FAST_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
# Writes code (fix proposals). A separate role because it needs exact copying more than
# deep reasoning: Ultra kept truncating old_text at quotes; MiniMax produced valid edits
# 2/2 times on the same case and passes the smoke test's code_in_tools check.
CODE_MODEL = os.environ.get("ETLDOC_CODE_MODEL", "minimaxai/minimax-m3.1-flash")


def make_model(name: str) -> OpenAIChatModel:
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        raise RuntimeError("NVIDIA_API_KEY is not set")
    # The free endpoint returns 429/500/503 under load. The OpenAI SDK retries those with
    # exponential backoff; the default of 2 retries is too few for a shared free tier.
    client = AsyncOpenAI(base_url=NVIDIA_BASE_URL, api_key=key, max_retries=6, timeout=180)
    provider = OpenAIProvider(openai_client=client)
    return OpenAIChatModel(name, provider=provider)
