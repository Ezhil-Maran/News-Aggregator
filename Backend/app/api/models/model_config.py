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
# 768 tokens are sufficient for a complete professional news article.
MAX_NEW_TOKENS = 768

# Greedy decoding produces deterministic and repeatable articles.
# This is preferred for factual news generation.
DO_SAMPLE = False

# These parameters are only used when sampling is enabled.
# They are kept here for future experimentation.
TEMPERATURE = 0.1
TOP_P = 1.0

# Helps reduce repetitive wording.
REPETITION_PENALTY = 1.1

# ============================================================
# CONTEXT
# ============================================================

# Maximum prompt length accepted by the model.
MAX_INPUT_LENGTH = 4096

# ============================================================
# DEBUG
# ============================================================

PRINT_MODEL_LOADING = True