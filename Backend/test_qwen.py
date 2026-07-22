from app.services.inference import generate_text

prompt = """
Explain Artificial Intelligence in one paragraph.
"""

response = generate_text(prompt)

print("\n================ RESPONSE ================\n")

print(response)