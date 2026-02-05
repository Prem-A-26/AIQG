import os
import json
import time
from groq import Groq

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ✅ UPDATED SUPPORTED MODEL
MODEL = "llama-3.1-8b-instant"

def generate_questions(prompt: str):
    """
    Calls Groq LLM with retry + strict JSON enforcement
    """

    for attempt in range(2):
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You must return ONLY valid JSON. No text outside JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=3000
        )

        text = completion.choices[0].message.content.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            if attempt == 0:
                # Retry once with stricter instruction
                prompt += "\n\nIMPORTANT: OUTPUT ONLY RAW JSON. DO NOT EXPLAIN."
                time.sleep(1)
            else:
                raise ValueError("LLM failed to return valid JSON")
