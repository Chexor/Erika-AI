import requests
import base64
import re
import pathlib
import logging
from .config import JOY_CONFIG, JOY_INSTRUCTIONS

class ErikaVision:
    def __init__(self, base_url=None, model_name=None):
        self.base_url = base_url or JOY_CONFIG["ollama_url"]
        self.model_name = model_name or JOY_CONFIG["model"]
        self.logger = logging.getLogger("ErikaVision")

    def clean_caption(self, text):
        # Remove common artifacts
        text = re.sub(r'(?i)^(here is a|this is a|a photo of|an image of)\s+', '', text)
        text = text.strip()
        return text

    def see(self, image_path: str) -> str:
        path = pathlib.Path(image_path)
        if not path.exists():
            return "Error: Image file not found."

        try:
            # Encode image
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # Prepare Payload
            # JoyAction uses standard generate endpoint with image
            # We default to the non-closeup prompt for general usage, 
            # or could analyze filename/metadata to switch. For now, general.
            prompt = JOY_INSTRUCTIONS["safe"]["non_closeup"]

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "images": [encoded_string],
                "stream": False,
                "options": {
                    "stop": JOY_CONFIG["stop_tokens"]
                }
            }

            response = requests.post(self.base_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                raw_caption = result.get("response", "")
                return self.clean_caption(raw_caption)
            else:
                return f"Error from Ollama: {response.text}"

        except Exception as e:
            self.logger.error(f"Vision Error: {e}")
            return f"Vision Error: {e}"
