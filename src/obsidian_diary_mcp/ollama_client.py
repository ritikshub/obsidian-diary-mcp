"""Ollama API client for text generation."""

import httpx
from .config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT, OLLAMA_TEMPERATURE, OLLAMA_NUM_PREDICT


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self):
        self.url = OLLAMA_URL
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT
    
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate text using Ollama API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"{system_prompt}\n\n{prompt}",
                    "stream": False,
                    "options": {
                        "temperature": OLLAMA_TEMPERATURE,
                        "num_predict": OLLAMA_NUM_PREDICT,
                    }
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
    
    def test_connection(self) -> bool:
        """Test if Ollama is available."""
        try:
            httpx.get(f"{self.url}/api/tags", timeout=2)
            return True
        except Exception:
            return False


ollama_client = OllamaClient()


def initialize_ollama():
    """Initialize and test Ollama connection."""
    if ollama_client.test_connection():
        print(f"✅ Ollama available at {OLLAMA_URL} with model {OLLAMA_MODEL}")
    else:
        print(f"Warning: Ollama not available at {OLLAMA_URL}")
        print("💡 Install Ollama and run: ollama pull llama3.1")