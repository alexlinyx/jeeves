# Feature Spec: Response Generator

**Phase:** 2.3  
**Branch:** `feature/2.3-response-generator`  
**Priority:** P0 (Blocking)  
**Est. Time:** 18 hours

---

## Objective

Build the response generation system that uses the LLM + RAG pipeline to generate email drafts with context from past emails and specified tone modes.

---

## Acceptance Criteria

- [ ] `src/response_generator.py` implements ResponseGenerator class
- [ ] `generate_reply(incoming_email, tone)` method works
- [ ] Tone modes: casual, formal, concise, match_style
- [ ] Integrates with LLM (from 2.1) and RAG (from 2.2)
- [ ] Tests verify all tone modes
- [ ] Tests verify RAG context inclusion
- [ ] Unit tests pass

---

## Deliverable

### `src/response_generator.py`

```python
"""Response generator using LLM + RAG for email drafting."""
from typing import List, Dict, Optional


class ResponseGenerator:
    """Generate email responses using LLM and RAG context."""
    
    # Tone configurations
    TONES = {
        "casual": {
            "system_prompt": "You are writing a casual, friendly email. Use contractions, be warm, keep it conversational.",
            "max_length": 200,
        },
        "formal": {
            "system_prompt": "You are writing a formal professional email. Use proper grammar, be polite, maintain a professional tone.",
            "max_length": 300,
        },
        "concise": {
            "system_prompt": "You are writing a brief, to-the-point email. Get straight to the answer, minimize fluff.",
            "max_length": 100,
        },
        "match_style": {
            "system_prompt": "You are writing an email that matches the user's personal writing style from their past emails.",
            "max_length": 250,
        },
    }
    
    def __init__(
        self,
        llm=None,
        rag=None,
        default_tone: str = "match_style",
        include_context: bool = True,
        context_top_k: int = 5
    ):
        """Initialize response generator."""
        pass
    
    def generate_reply(
        self,
        incoming_email: Dict,
        tone: str = None,
        custom_prompt: str = None
    ) -> str:
        """Generate a reply to an incoming email."""
        pass
    
    def generate_with_context(
        self,
        incoming_email: Dict,
        context_emails: List[Dict]
    ) -> str:
        """Generate response with explicit context emails."""
        pass
    
    def set_tone(self, tone: str):
        """Set default tone for responses."""
        pass
    
    def get_available_tones(self) -> List[str]:
        """Get list of available tone modes."""
        pass
    
    def _build_prompt(self, incoming_email: Dict, context: List[str] = None, tone: str = None, custom: str = None) -> tuple:
        """Build prompt for LLM."""
        pass
    
    def _get_style_from_past_emails(self, from_email: str) -> str:
        """Analyze user's past emails to determine writing style."""
        pass


# Convenience functions

def generate_reply(incoming_email: Dict, tone: str = None, **kwargs) -> str:
    """Quick function to generate a reply."""
    gen = ResponseGenerator(**kwargs)
    return gen.generate_reply(incoming_email, tone)
```

---

## Testing Requirements

### Unit Tests (tests/test_response_generator.py)

The tests must verify:

1. **File & Import Tests**
   - `test_file_exists` - src/response_generator.py exists
   - `test_import` - ResponseGenerator can be imported

2. **Method Tests**
   - `test_class_has_required_methods` - generate_reply, generate_with_context, set_tone, get_available_tones
   - `test_convenience_function_exists` - generate_reply() function exists

3. **Tone Tests**
   - `test_tone_modes_defined` - All 4 tones exist: casual, formal, concise, match_style
   - `test_tones_dict_structure` - Each tone has system_prompt and max_length
   - `test_default_tone` - Default is 'match_style'
   - `test_set_tone` - set_tone() changes default
   - `test_get_available_tones` - Returns list of 4 tone names

4. **Integration Tests**
   - `test_llm_integration` - LLM is called for generation
   - `test_rag_integration` - RAG context is included
   - `test_tone_affects_prompt` - Different tones produce different prompts

5. **Edge Case Tests**
   - `test_empty_email_handling` - Missing email fields handled gracefully

6. **Dependency Tests**
   - `test_requirements_have_dependencies` - Required packages in requirements.txt

---

## Tasks

### 2.3.1 Build ResponseGenerator Class (8 hrs)
- [ ] Implement __init__ with LLM/RAG integration
- [ ] Define TONES dictionary with prompts
- [ ] Implement generate_reply() with tone selection
- [ ] Implement generate_with_context()
- [ ] Implement set_tone() and get_available_tones()

### 2.3.2 Prompt Building (4 hrs)
- [ ] Implement _build_prompt() 
- [ ] Handle tone injection
- [ ] Handle context inclusion
- [ ] Handle custom prompts

### 2.3.3 Style Matching (4 hrs)
- [ ] Implement _get_style_from_past_emails()
- [ ] Query RAG for user's sent emails
- [ ] Extract style characteristics

### 2.3.4 Write Tests (2 hrs)
- [ ] Write all tests per testing requirements
- [ ] Run and fix failures

---

## Dependencies

| Dependency | Purpose |
|------------|---------|
| src.llm | LLM wrapper from 2.1 |
| src.rag | RAG pipeline from 2.2 |

---

## Testing

```bash
# Run tests
pytest tests/test_response_generator.py -v

# Test generation
python -c "
from src.response_generator import ResponseGenerator
email = {'subject': 'Meeting?', 'from': 'bob@example.com', 'body_text': 'Are we still meeting tomorrow?'}
gen = ResponseGenerator()
draft = gen.generate_reply(email, tone='formal')
print(draft)
"
```

---

## Notes

- Response generator depends on 2.1 (LLM) and 2.2 (RAG) being complete
- Tone prompts can be customized in .env or config
- max_length is a guideline, LLM may exceed slightly

---

## Definition of Done

1. `src/response_generator.py` implements ResponseGenerator
2. All 4 tone modes work
3. RAG context is included in generation
4. All unit tests pass (minimum 12 tests)
5. Branch pushed to GitHub
6. PR created
