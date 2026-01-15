
JOY_CONFIG = {
    "closeup_keywords": ['close-up', 'zoom', 'detail', 'macro'],
    "stop_tokens": ["\n", ".", "</s>"],
    "ollama_url": "http://localhost:11434/api/generate",
    "model": "joycaption" # User default, falls back to llava if needed in logic
}

JOY_INSTRUCTIONS = {
    "safe": {
        "closeup": "Describe this close-up image in detail. Focus on textures and lighting.",
        "non_closeup": "Describe this image in detail. Focus on the main subject and background."
    }
}
