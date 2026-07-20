from app.api.models.qwen_loader import load_model

print("Loading Qwen...")

tokenizer, model = load_model()

print("\nEverything loaded successfully!")