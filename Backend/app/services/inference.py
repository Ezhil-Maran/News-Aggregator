"""
inference.py

Provides a simple interface for generating text using Qwen.

All interactions with the LLM should go through this module.
"""

import torch

from app.api.models.qwen_loader import load_model
from app.api.models.model_config import (
    MAX_NEW_TOKENS,
    TEMPERATURE,
    TOP_P,
    TOP_K,
    DO_SAMPLE,
    REPETITION_PENALTY,
)

# ============================================================
# GENERATE TEXT
# ============================================================

def generate_text(prompt: str) -> str:

    tokenizer, model = load_model()

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
    )

    # Move tensors to the correct device
    inputs = {
        key: value.to(model.device)
        for key, value in inputs.items()
    }

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            do_sample=DO_SAMPLE,
            repetition_penalty=REPETITION_PENALTY,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated_text = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    # Remove the original prompt from the output if present.
    if generated_text.startswith(prompt):
        generated_text = generated_text[len(prompt):].strip()

    return generated_text