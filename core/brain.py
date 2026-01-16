from core.llm.engine import LocalLLMEngine
from core.erika_vision.engine import ErikaVision
from core.logger import setup_logger
from core.settings import SettingsManager

class Brain:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Brain, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.logger = setup_logger("Brain")
        self.settings_manager = SettingsManager()

        # Retrieve LLM configuration from settings manager, with fallbacks
        llm_base_url = self.settings_manager.get_system_setting("ollama_url", "http://localhost:11434")
        # Ensure the URL ends with /v1 for the OpenAI API compatibility
        if not llm_base_url.endswith("/v1"):
            llm_base_url += "/v1"
        
        llm_model_name = self.settings_manager.get_system_setting("model", "llama3")

        self.engine = LocalLLMEngine(base_url=llm_base_url, model_name=llm_model_name)
        self.vision = ErikaVision() # Initialize Vision
        # Default persona fallback, but we primarily use settings now
        self.default_persona = (
            "You are Erika, a highly capable local AI assistant. "
            "You are helpful, concise, and run entirely on the user's hardware."
        )
        self.logger.info(f"Initialized Brain with model: {llm_model_name}")
        self._initialized = True

    def _get_system_prompt(self):
        return self.settings_manager.get_user_setting('persona', self.default_persona)

    async def think(self, user_input, system_prompt=None):
        persona = system_prompt if system_prompt else self._get_system_prompt()
        self.logger.info(f"Thinking on input: {str(user_input)[:50]}...")
        try:
            return await self.engine.generate(user_input, persona)
        except Exception as e:
            self.logger.error(f"Error in think: {e}", exc_info=True)
            return "Thinking Error."

    async def think_stream(self, user_input, system_prompt=None):
        persona = system_prompt if system_prompt else self._get_system_prompt()
        self.logger.info(f"Streaming on input: {str(user_input)[:50]}...")
        try:
            async for chunk in self.engine.stream(user_input, persona):
                yield chunk
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
