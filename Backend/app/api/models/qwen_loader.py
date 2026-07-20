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

        if PRINT_MODEL_LOADING:
            print(f"\nLoading model: {MODEL_PATH}")

        print("Loading tokenizer...")

        tokenizer = AutoTokenizer.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True
        )

        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        print("Tokenizer loaded successfully.")

        print(f"Using device: {DEVICE}")

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

            print("Loading model...")

            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
                dtype=torch.float16,
            )

        # ----------------------------------------------------
        # CPU
        # ----------------------------------------------------

        else:

            print("Loading model on CPU...")

            model = AutoModelForCausalLM.from_pretrained(
                MODEL_PATH,
                trust_remote_code=True,
                dtype=torch.float32,
            )

            model.to(DEVICE)

        model.eval()

        print("Model loaded successfully!")

        return tokenizer, model

    except Exception:

        print("\n========== MODEL LOADING FAILED ==========\n")

        traceback.print_exc()

        print("\n==========================================\n")

        raise