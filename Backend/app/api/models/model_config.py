"""
model_config.py

Central configuration for all Large Language Models used in the project.

Changing the model or generation behaviour should only require
editing this file.
"""

import torch

# ============================================================
# MODEL CONFIGURATION
# ============================================================

# Hugging Face model repository
MODEL_NAME = "Qwen/Qwen3-4B"

# If you later fine-tune the model,
# simply change this path to your fine-tuned adapter/model.
MODEL_PATH = MODEL_NAME

# ============================================================
# DEVICE CONFIGURATION
# ============================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ============================================================
# GENERATION PARAMETERS
# ============================================================

MAX_NEW_TOKENS = 1024

TEMPERATURE = 0.3

TOP_P = 0.9

TOP_K = 50

DO_SAMPLE = True

REPETITION_PENALTY = 1.1

# ============================================================
# CONTEXT
# ============================================================

# Maximum number of input tokens.
# We may increase or decrease this later after testing.
MAX_INPUT_LENGTH = 4096

# ============================================================
# PROMPT SETTINGS
# ============================================================

SYSTEM_PROMPT = """
You are an experienced professional journalist.

Your task is to construct ONE coherent news article from
multiple news reports.

Rules:

- Preserve factual accuracy.
- Do NOT invent information.
- Remove duplicate information.
- Merge similar facts together.
- Maintain a neutral journalistic tone.
- Organize the article logically.
- Preserve important names, places and dates.
- Produce a professional article rather than bullet points.
"""

# ============================================================
# DEBUG
# ============================================================

PRINT_MODEL_LOADING = True