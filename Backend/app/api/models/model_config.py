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

# Change this later if you fine-tune the model.
MODEL_PATH = MODEL_NAME

# ============================================================
# DEVICE CONFIGURATION
# ============================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ============================================================
# GENERATION PARAMETERS
# ============================================================

# Maximum number of tokens the model can generate.
# This is sufficient for a professional news article.
MAX_NEW_TOKENS = 768

# Lower temperature reduces creativity and hallucinations.
# Ideal for factual news generation.
TEMPERATURE = 0.1

# Consider the full probability distribution.
TOP_P = 1.0

# Kept for future experimentation.
TOP_K = 50

# Disable sampling for deterministic, reproducible outputs.
DO_SAMPLE = False

# Discourages repetitive wording.
REPETITION_PENALTY = 1.1

# ============================================================
# CONTEXT
# ============================================================

MAX_INPUT_LENGTH = 4096

# ============================================================
# DEBUG
# ============================================================

PRINT_MODEL_LOADING = True