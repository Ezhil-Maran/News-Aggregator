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

from app.prompts.system_prompt import SYSTEM_PROMPT


# ============================================================
# GENERATE TEXT
# ============================================================

def generate_text(user_prompt: str) -> str:

    print("\n========== STEP 5 ==========")
    print("Entered generate_text()")
    print("============================\n")

    print("STEP 6: Calling load_model()...")

    tokenizer, model = load_model()

    print("STEP 7: Model loaded successfully.")

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

    print("STEP 8: Applying chat template...")

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    print("STEP 9: Tokenizing prompt...")

    inputs = tokenizer(
        text,
        return_tensors="pt",
    )

    inputs = {
        key: value.to(model.device)
        for key, value in inputs.items()
    }

    print("STEP 10: Starting model.generate()...")

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

    print("STEP 11: Generation complete.")

    generated_text = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True,
    )

    generated_text = generated_text[len(text):].strip()

    print("STEP 12: Response decoded.\n")

    return generated_text