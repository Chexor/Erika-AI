from core.llm.engine import LocalLLMEngine
from core.erika_vision.engine import ErikaVision

# CONFIG: Default to Ollama. Change model_name if needed.
ACTIVE_URL = "http://localhost:11434/v1"
ACTIVE_MODEL = "llama3" 

class Brain:
    def __init__(self):
        self.engine = LocalLLMEngine(base_url=ACTIVE_URL, model_name=ACTIVE_MODEL)
        self.vision = ErikaVision() # Initialize Vision
        self.system_persona = (
            "You are Erika, a highly capable local AI assistant. "
            "You are helpful, concise, and run entirely on the user's hardware."
        )

    def think(self, user_input):
        return self.engine.generate(user_input, self.system_persona)

    def think_stream(self, user_input):
        return self.engine.stream(user_input, self.system_persona)
        
    def status_check(self) -> bool:
        return self.engine.check_connection()

    def get_model_name(self) -> str:
        return self.engine.model_name
        
    def analyze_image(self, image_path: str):
        """Passes the image to Erika-vision and returns the description."""
        return self.vision.see(image_path)
