"""
inference.py

Provides interfaces for generating text and news articles using Qwen.

All interactions with the LLM should go through this module.
"""

from typing import Dict, List

import torch

from app.api.models.model_config import (
    DO_SAMPLE,
    MAX_NEW_TOKENS,
    REPETITION_PENALTY,
    TEMPERATURE,
    TOP_K,
    TOP_P,
)
from app.api.models.qwen_loader import load_model
from app.prompts.prompt_builder import build_news_prompt
from app.prompts.system_prompt import SYSTEM_PROMPT


# ============================================================
# LOW-LEVEL TEXT GENERATION
# ============================================================

def generate_text(prompt: str) -> str:
    """
    Generates text from a user prompt.

    Parameters
    ----------
    prompt : str
        User prompt.

    Returns
    -------
    str
        Model-generated response.
    """

    tokenizer, model = load_model()

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
    )

    inputs = inputs.to(model.device)

    with torch.inference_mode():

        outputs = model.generate(
            inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            do_sample=DO_SAMPLE,
            repetition_penalty=REPETITION_PENALTY,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = outputs[0][inputs.shape[-1]:]

    generated_text = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )

    return generated_text.strip()


# ============================================================
# HIGH-LEVEL NEWS ARTICLE GENERATION
# ============================================================

def generate_article(cluster: List[Dict]) -> str:
    """
    Generates a single consolidated news article from a cluster
    of related news articles.

    Parameters
    ----------
    cluster : List[Dict]
        Cluster of related articles.

    Returns
    -------
    str
        AI-generated news article.
    """

    prompt = build_news_prompt(cluster)

    return generate_text(prompt)