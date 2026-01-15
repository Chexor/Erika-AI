from core.llm.engine import LocalLLMEngine
from core.erika_vision.engine import ErikaVision
from core.logger import setup_logger

# CONFIG: Default to Ollama. Change model_name if needed.
ACTIVE_URL = "http://localhost:11434/v1"
ACTIVE_MODEL = "llama3" 

class Brain:
    def __init__(self):
        self.logger = setup_logger("Brain")
        self.engine = LocalLLMEngine(base_url=ACTIVE_URL, model_name=ACTIVE_MODEL)
        self.vision = ErikaVision() # Initialize Vision
        self.system_persona = (
            "You are Erika, a highly capable local AI assistant. "
            "You are helpful, concise, and run entirely on the user's hardware."
        )
        self.logger.info(f"Initialized Brain with model: {ACTIVE_MODEL}")

    def think(self, user_input):
        self.logger.info(f"Thinking on input: {str(user_input)[:50]}...")
        try:
            return self.engine.generate(user_input, self.system_persona)
        except Exception as e:
            self.logger.error(f"Error in think: {e}", exc_info=True)
            return "Thinking Error."

    def think_stream(self, user_input):
        self.logger.info(f"Streaming on input: {str(user_input)[:50]}...")
        try:
            return self.engine.stream(user_input, self.system_persona)
        except Exception as e:
            self.logger.error(f"Error in think_stream: {e}", exc_info=True)
            yield "Stream Error."
        
    def status_check(self) -> bool:
        status = self.engine.check_connection()
        self.logger.debug(f"Status Check: {status}")
        return status

    def get_model_name(self) -> str:
        return self.engine.model_name
        
    def analyze_image(self, image_path: str):
        """Passes the image to Erika-vision and returns the description."""
        self.logger.info(f"Analyzing image: {image_path}")
        return self.vision.see(image_path)
