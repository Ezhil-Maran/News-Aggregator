"""
qwen_loader.py

Loads the Qwen model and tokenizer.

The model is loaded only once when the backend starts.
"""

import traceback
import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

from app.api.models.model_config import (
    MODEL_PATH,
    DEVICE,
    PRINT_MODEL_LOADING,
)

# ============================================================
# GLOBAL VARIABLES
# ============================================================

tokenizer = None
model = None

# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    global tokenizer
    global model

    if model is not None and tokenizer is not None:
        return tokenizer, model

    try:

        print("\n========== QWEN INITIALIZATION ==========\n")

        if PRINT_MODEL_LOADING:
            print(f"Model: {MODEL_PATH}")

        print("Loading tokenizer...")

        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        print("Tokenizer loaded successfully.")

        print(f"Using device : {DEVICE}")

        if DEVICE == "cuda":
            print(f"GPU          : {torch.cuda.get_device_name(0)}")

            total_vram = (
                torch.cuda.get_device_properties(0).total_memory
                / (1024 ** 3)
            )

            print(f"VRAM         : {total_vram:.2f} GB")

        print()

        # ----------------------------------------------------
        # GPU
        # ----------------------------------------------------

        if DEVICE == "cuda":

            print("Preparing 4-bit quantization...")

            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )

            print("Loading Qwen model...")

            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                quantization_config=quantization_config,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True,
            )

        # ----------------------------------------------------
        # CPU
        # ----------------------------------------------------

        else:

            print("Loading model on CPU...")

            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                torch_dtype=torch.float32,
                trust_remote_code=True,
            )

            model.to(DEVICE)

        model.eval()

        print("\nQwen initialized successfully.")
        print("\n=========================================\n")

        return tokenizer, model

    except Exception:

        print("\n========== MODEL LOADING FAILED ==========\n")

        traceback.print_exc()

        print("\n==========================================\n")

        raise