# Feature Spec: LLM Setup

**Phase:** 2.1  
**Branch:** `feature/2.1-llm-setup`  
**Priority:** P0 (Blocking)  
**Est. Time:** 5 hours

---

## Objective

Set up local LLM inference using Ollama and create a Python wrapper for generating email responses.

---

## Acceptance Criteria

- [ ] Ollama installed and running
- [ ] Base model pulled (`mistral:7b-instruct` or similar)
- [x] `src/llm.py` implements LLM wrapper class
- [x] `python -c "from src.llm import LLM; print(LLM().generate('Hello'))"` works (needs Ollama)
- [x] Unit tests pass

---

## Deliverable

### `src/llm.py`

```python
"""Local LLM wrapper using Ollama."""
import os
import json
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
        """Initialize LLM wrapper.
        
        Args:
            model: Model name (default: mistral:7b-instruct)
            base_url: Ollama API base URL
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
        """
        self.model = model or os.environ.get('OLLAMA_MODEL', self.DEFAULT_MODEL)
        self.base_url = base_url or os.environ.get('OLLAMA_BASE_URL', self.DEFAULT_BASE_URL)
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate text from prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
        """
        pass
    
    def generate_with_context(
        self,
        prompt: str,
        context_docs: List[str],
        system_prompt: str = None
    ) -> str:
        """Generate text with RAG context.
        
        Args:
            prompt: User prompt
            context_docs: List of relevant documents to include
            system_prompt: Optional system prompt
            
        Returns:
            Generated text
        """
        pass
    
    def chat(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """Chat completion style interface.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            
        Returns:
            Assistant response
        """
        pass
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available.
        
        Returns:
            True if LLM is accessible
        """
        pass
    
    def list_models(self) -> List[str]:
        """List available models.
        
        Returns:
            List of model names
        """
        pass


# Convenience functions

def generate(prompt: str, **kwargs) -> str:
    """Quick generate function.
    
    Args:
        prompt: User prompt
        **kwargs: Additional args passed to LLM.generate()
        
    Returns:
        Generated text
    """
    llm = LLM(**kwargs)
    return llm.generate(prompt)


def generate_with_context(prompt: str, context_docs: List[str], **kwargs) -> str:
    """Quick generate with context function.
    
    Args:
        prompt: User prompt
        context_docs: Documents to include as context
        **kwargs: Additional args
        
    Returns:
        Generated text
    """
    llm = LLM(**kwargs)
    return llm.generate_with_context(prompt, context_docs)
```

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama API URL |
| `OLLAMA_MODEL` | mistral:7b-instruct | Default model |
| `OLLAMA_TEMPERATURE` | 0.7 | Generation temperature |

### Model Options

Recommended models for email assistant:
- `mistral:7b-instruct` - Fast, good quality (recommended)
- `llama2:7b` - Meta's model
- `mixtral:8x7b` - More powerful, needs more RAM
- `phi:2.7b` - Lightweight option

---

## Tasks

### 2.1.1 Install Ollama (30 min)
- [ ] Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
- [ ] Start Ollama service: `ollama serve`
- [ ] Verify running: `ollama list`

### 2.1.2 Pull Base Model (10 min)
- [ ] Pull model: `ollama pull mistral:7b-instruct`
- [ ] Test: `ollama run mistral:7b-instruct "Hello"`

### 2.1.3 Build LLM Wrapper (3 hrs)
- [ ] Implement `LLM` class with all methods
- [ ] Handle API calls to Ollama
- [ ] Add error handling
- [ ] Add retry logic for failures

### 2.1.4 Test Integration (1 hr)
- [ ] Test: `python -c "from src.llm import LLM; print(LLM().generate('Hello'))"`
- [ ] Test with longer prompts
- [ ] Test with context

### 2.1.5 Unit Tests (30 min)
- [ ] Test LLM class initialization
- [ ] Test generate method
- [ ] Test is_available method
- [ ] Mock tests for API calls

---

## Dependencies

| Dependency | Purpose |
|------------|---------|
| requests | HTTP calls to Ollama API |
| python-dotenv | Environment variable loading |

---

## Testing

```bash
# Test basic generation
python -c "from src.llm import LLM; print(LLM().generate('Hello'))"

# Test with context
python -c "
from src.llm import LLM
llm = LLM()
docs = ['Previous email: Thanks for the update!', 'Your writing style is concise.']
print(llm.generate_with_context('Draft a reply to the project update', docs))
"

# Test chat
python -c "
from src.llm import LLM
llm = LLM()
messages = [
    {'role': 'user', 'content': 'Hello'},
]
print(llm.chat(messages))
"

# Test availability
python -c "from src.llm import LLM; print(LLM().is_available())"

# Run tests
pytest tests/test_llm.py -v
```

---

## Notes

- Ollama must be running locally (or accessible via network)
- First model pull takes time (GBs)
- GPU recommended but CPU works (slower)
- Model stays loaded in memory for fast inference

---

## Definition of Done

1. Ollama installed and model pulled
2. `src/llm.py` implements LLM wrapper
3. `python -c "from src.llm import LLM; print(LLM().generate('Hello'))"` succeeds
4. `generate_with_context()` works with RAG docs
5. `chat()` works with message history
6. Unit tests pass
7. Branch pushed to GitHub
8. PR created
