import google.generativeai as genai
import logging
from .interfaces import ModelClient

logger = logging.getLogger(__name__)

class GeminiProClient(ModelClient):
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key is required for Gemini Pro")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini Pro Generation Error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        try:
            return self.model.count_tokens(text).total_tokens
        except:
            return len(text) // 4 # Fallback

class GeminiFlashClient(ModelClient):
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key is required for Gemini Flash")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.token_limit = 8000 # Configurable limit for Flash context

    def generate(self, prompt: str) -> str:
        try:
            # Token Count & Truncation Logic
            current_tokens = self.count_tokens(prompt)
            
            if current_tokens > self.token_limit:
                logger.warning(f"⚠️ Prompt exceeds Flash limit ({current_tokens}/{self.token_limit}). Truncating.")
                # Simple truncation strategy: keep beginning and instructions, truncate middle? 
                # Or just safe cut. For stability, we cut the end but keep instructions if possible.
                # Assuming prompt structure is Instructions + Content.
                # Heuristic: Cut to size based on chars (~4 chars per token)
                max_chars = self.token_limit * 4
                prompt = prompt[:max_chars] + "\n[...TRUNCATED FOR FLASH LIMIT...]"
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini Flash Generation Error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        try:
            return self.model.count_tokens(text).total_tokens
        except:
            return len(text) // 4
