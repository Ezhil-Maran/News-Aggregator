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
MODEL_NAME = "Qwen/Qwen3-4B-Instruct"

# Change this later if you fine-tune the model.
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

MAX_INPUT_LENGTH = 4096

# ============================================================
# DEBUG
# ============================================================

PRINT_MODEL_LOADING = True