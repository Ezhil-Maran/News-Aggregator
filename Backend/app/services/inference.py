"""
inference.py

Centralized interface for generating text using Qwen.
"""

import time
import torch
from app.api.models.qwen_loader import load_model

from app.api.models.model_config import (
    MAX_NEW_TOKENS,
    MAX_INPUT_LENGTH,
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

    print("\n" + "=" * 60)
    print("QWEN GENERATION STARTED")
    print("=" * 60)

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    print("[1/7] Loading Qwen model...")

    load_start = time.time()

    tokenizer, model = load_model()

    print(
        f"[1/7] Model loaded in "
        f"{time.time() - load_start:.2f}s"
    )

    # --------------------------------------------------------
    # Build chat messages
    # --------------------------------------------------------

    print("[2/7] Building chat prompt...")

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
    enable_thinking=False,
)

    print(
        f"[2/7] Prompt characters: "
        f"{len(prompt):,}"
    )

    # --------------------------------------------------------
    # Tokenize
    # --------------------------------------------------------

    print("[3/7] Tokenizing prompt...")

    tokenize_start = time.time()

    inputs = tokenizer(
    prompt,
    return_tensors="pt",
    truncation=True,
    max_length=MAX_INPUT_LENGTH,
)

    print(
        f"[3/7] Tokenization completed in "
        f"{time.time() - tokenize_start:.2f}s"
    )

    input_token_count = inputs["input_ids"].shape[1]

    print(
    f"[3/7] Input token limit: "
    f"{MAX_INPUT_LENGTH:,}"
)
    
    print(
        f"[3/7] Input tokens: "
        f"{input_token_count:,}"
    )

    # --------------------------------------------------------
    # Move inputs to model device
    # --------------------------------------------------------

    print("[4/7] Moving inputs to model device...")

    print(f"[4/7] Model device: {model.device}")

    inputs = {
        key: value.to(model.device)
        for key, value in inputs.items()
    }

    print("[4/7] Inputs moved successfully.")

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

    if DO_SAMPLE:
        generation_kwargs.update({
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
        })

    print("[5/7] Generation configuration:")
    print(f"       max_new_tokens = {MAX_NEW_TOKENS}")
    print(f"       do_sample      = {DO_SAMPLE}")

    if DO_SAMPLE:
        print(f"       temperature    = {TEMPERATURE}")
        print(f"       top_p          = {TOP_P}")

    print(f"       repetition     = {REPETITION_PENALTY}")

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    print("\n[6/7] BEFORE model.generate()")
    print("      Qwen is now generating...")
    print("      This may take some time on the RTX 3050.\n")

    generation_start = time.time()

    with torch.inference_mode():

        outputs = model.generate(
            **inputs,
            **generation_kwargs,
        )

    generation_time = time.time() - generation_start

    print(
        f"\n[6/7] AFTER model.generate()"
    )

    print(
        f"[6/7] Generation time: "
        f"{generation_time:.2f}s"
    )

    # --------------------------------------------------------
    # Decode
    # --------------------------------------------------------

    print("[7/7] Decoding generated tokens...")

    generated_tokens = outputs[
        0
    ][
        inputs["input_ids"].shape[1]:
    ]

    print(
        f"[7/7] Generated tokens: "
        f"{generated_tokens.shape[0]:,}"
    )

    generated_text = tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    )

    print("[7/7] Decoding completed.")

    print("\n" + "=" * 60)
    print("QWEN GENERATION COMPLETED")
    print("=" * 60 + "\n")

    return generated_text.strip()