"""Local LLM wrapper using Ollama."""
import os
import json
import requests
from typing import List, Dict, Optional


class LLM:
    """Ollama LLM wrapper for generating email responses."""
    
    DEFAULT_MODEL = "mistral:7b-instruct"
    DEFAULT_BASE_URL = "http://localhost:11434"
    
    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """Initialize LLM wrapper."""
        self.model = model or os.environ.get('OLLAMA_MODEL', self.DEFAULT_MODEL)
        self.base_url = base_url or os.environ.get('OLLAMA_BASE_URL', self.DEFAULT_BASE_URL)
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def _make_request(self, endpoint: str, payload: dict) -> dict:
        """Make request to Ollama API."""
        url = f"{self.base_url}/api/{endpoint}"
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Ollama is not running. Start with: ollama serve")
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}")
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text from prompt."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "options": {"num_predict": self.max_tokens}
        }
        if system_prompt:
            payload["system"] = system_prompt
        
        result = self._make_request("generate", payload)
        return result.get('response', '').strip()
    
    def generate_with_context(
        self,
        prompt: str,
        context_docs: List[str],
        system_prompt: str = None
    ) -> str:
        """Generate text with RAG context."""
        context = "\n\n".join(f"Context {i+1}:\n{doc}" for i, doc in enumerate(context_docs))
        
        full_prompt = f"""Based on the following context, answer the user's question.

{context}

---

User question: {prompt}

Answer:"""
        
        return self.generate(full_prompt, system_prompt)
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat completion style interface."""
        # Convert messages to Ollama format
        ollama_messages = []
        system_msg = None
        
        for msg in messages:
            if msg.get('role') == 'system':
                system_msg = msg.get('content')
            else:
                ollama_messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })
        
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "temperature": self.temperature,
            "options": {"num_predict": self.max_tokens}
        }
        if system_msg:
            payload["system"] = system_msg
        
        result = self._make_request("chat", payload)
        return result.get('message', {}).get('response', '').strip()
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            # Try to list models
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m.get('name', '').split(':')[0] for m in models]
                return self.model.split(':')[0] in model_names
            return False
        except:
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m.get('name', '') for m in models]
            return []
        except Exception as e:
            return []


# Convenience functions

def generate(prompt: str, **kwargs) -> str:
    """Quick generate function."""
    llm = LLM(**kwargs)
    return llm.generate(prompt)


def generate_with_context(prompt: str, context_docs: List[str], **kwargs) -> str:
    """Quick generate with context function."""
    llm = LLM(**kwargs)
    return llm.generate_with_context(prompt, context_docs)
