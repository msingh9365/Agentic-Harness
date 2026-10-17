"""One place that knows how to talk to the LLM provider.

NVIDIA's API (build.nvidia.com) speaks the OpenAI Chat Completions protocol, so we reuse
PydanticAI's OpenAI model class and only swap the base URL and key. Switching provider
later (Azure, OpenAI, a local vLLM) means changing this file, not the agents.
"""

import os

from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# Chosen from the smoke test in scripts/smoke_llm.py (results: docs/04-model-smoke-test.md).
STRONG_MODEL = os.environ.get("ETLDOC_STRONG_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
FAST_MODEL = os.environ.get("ETLDOC_FAST_MODEL", "openai/gpt-oss-20b")


def make_model(name: str) -> OpenAIChatModel:
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        raise RuntimeError("NVIDIA_API_KEY is not set")
    # The free endpoint returns 429/500/503 under load. The OpenAI SDK retries those with
    # exponential backoff; the default of 2 retries is too few for a shared free tier.
    client = AsyncOpenAI(base_url=NVIDIA_BASE_URL, api_key=key, max_retries=6, timeout=180)
    provider = OpenAIProvider(openai_client=client)
    return OpenAIChatModel(name, provider=provider)
