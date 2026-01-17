import tiktoken
import logging

logger = logging.getLogger("ENGINE.TokenCounter")

class TokenCounter:
    _encoding_cache = None

    def __init__(self, model_name="cl100k_base"):
        if TokenCounter._encoding_cache is None:
            try:
                # Use cl100k_base (GPT-4) as a good general proxy
                TokenCounter._encoding_cache = tiktoken.get_encoding(model_name)
                logger.info(f"TokenCounter initialized with encoding: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to load tiktoken encoding '{model_name}': {e}. Falling back to simple word count approximation.")
                TokenCounter._encoding_cache = None
        
        self.encoding = TokenCounter._encoding_cache

    def count(self, text: str) -> int:
        """Returns the number of tokens in a text string."""
        if not text:
            return 0
        
        if self.encoding:
            try:
                return len(self.encoding.encode(text))
            except Exception as e:
                logger.error(f"Error encoding text: {e}")
                return len(text.split()) # Fallback
        else:
            # Fallback approximation: 1.3 tokens per word
            return int(len(text.split()) * 1.3) + 1

    def count_messages(self, messages: list) -> int:
        """
        Counts tokens for a list of messages.
        Includes overhead for message formatting (ChatML/OpenAI style).
        """
        tokens = 0
        # Overhead per message (approximate for most Chat models)
        # <|im_start|>{role}\n{content}<|im_end|>\n
        tokens_per_message = 3 
        
        for msg in messages:
            tokens += tokens_per_message
            for key, value in msg.items():
                if key == "content":
                    tokens += self.count(str(value))
                elif key == "role":
                    tokens += 1 # Role takes usually 1 token
                    
        tokens += 3  # Every reply is primed with <|im_start|>assistant<|im_sep|>
        return tokens
