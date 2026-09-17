"""
inference.py

Provides a centralized interface for generating text using Qwen.

All interactions with the language model should go through this module.
"""

import torch

from app.api.models.qwen_loader import load_model

from app.api.models.model_config import (
    MAX_NEW_TOKENS,
    TEMPERATURE,
    TOP_P,
    DO_SAMPLE,
    REPETITION_PENALTY,
)

from app.prompts.system_prompt import SYSTEM_PROMPT


# ============================================================
# GENERATE TEXT
# ============================================================

def generate_text(user_prompt: str) -> str:
    """
    Generates text using the loaded Qwen model.
    """

    tokenizer, model = load_model()

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    )

    inputs = {
        key: value.to(model.device)
        for key, value in inputs.items()
    }

    # --------------------------------------------------------
    # Generation configuration
    # --------------------------------------------------------

    generation_kwargs = {
        "max_new_tokens": MAX_NEW_TOKENS,
        "do_sample": DO_SAMPLE,
        "repetition_penalty": REPETITION_PENALTY,
        "pad_token_id": tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
    }

    # Sampling parameters are only used when sampling is enabled.
    if DO_SAMPLE:

        generation_kwargs.update({
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
        })

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            **generation_kwargs,
        )

    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]

    generated_text = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )

    return generated_text.strip()