"""Tests for LLM wrapper."""
import pytest
import os
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/jeeves')

from src.llm import LLM, generate, generate_with_context


class TestLLM:
    """Test cases for LLM wrapper."""
    
    def test_llm_file_exists(self):
        """Test llm.py exists."""
        assert os.path.exists('/home/ubuntu/.openclaw/workspace/jeeves/src/llm.py')
    
    def test_llm_import(self):
        """Test LLM can be imported."""
        from src.llm import LLM
        assert LLM is not None
    
    def test_class_has_required_methods(self):
        """Test LLM has all required methods."""
        required = ['generate', 'generate_with_context', 'chat', 'is_available', 'list_models']
        for method in required:
            assert hasattr(LLM, method), f"Missing method: {method}"
    
    def test_generate_function_exists(self):
        """Test convenience function exists."""
        assert callable(generate)
    
    def test_generate_with_context_function_exists(self):
        """Test convenience function exists."""
        assert callable(generate_with_context)
    
    def test_default_model(self):
        """Test default model is set."""
        llm = LLM()
        assert llm.model == "mistral:7b-instruct"
    
    def test_default_base_url(self):
        """Test default base URL."""
        llm = LLM()
        assert llm.base_url == "http://localhost:11434"
    
    def test_custom_model(self):
        """Test custom model can be set."""
        llm = LLM(model="llama2:7b")
        assert llm.model == "llama2:7b"
    
    def test_custom_temperature(self):
        """Test custom temperature."""
        llm = LLM(temperature=0.5)
        assert llm.temperature == 0.5
    
    def test_custom_max_tokens(self):
        """Test custom max tokens."""
        llm = LLM(max_tokens=100)
        assert llm.max_tokens == 100
    
    def test_requirements_have_requests(self):
        """Test requirements.txt has requests."""
        with open('/home/ubuntu/.openclaw/workspace/jeeves/requirements.txt', 'r') as f:
            content = f.read()
        assert 'requests' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])