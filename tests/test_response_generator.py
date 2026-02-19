"""Tests for Response Generator."""
import pytest
import os
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/jeeves')

from src.response_generator import ResponseGenerator, generate_reply


class TestResponseGenerator:
    """Test cases for ResponseGenerator."""
    
    def test_file_exists(self):
        """Test response_generator.py exists."""
        assert os.path.exists('/home/ubuntu/.openclaw/workspace/jeeves/src/response_generator.py')
    
    def test_import(self):
        """Test ResponseGenerator can be imported."""
        from src.response_generator import ResponseGenerator
        assert ResponseGenerator is not None
    
    def test_class_has_required_methods(self):
        """Test all required methods exist."""
        required = ['generate_reply', 'generate_with_context', 'set_tone', 'get_available_tones']
        for method in required:
            assert hasattr(ResponseGenerator, method), f"Missing method: {method}"
    
    def test_tone_modes_defined(self):
        """Test all 4 tone modes are defined."""
        expected_tones = {'casual', 'formal', 'concise', 'match_style'}
        assert hasattr(ResponseGenerator, 'TONES')
        assert set(ResponseGenerator.TONES.keys()) == expected_tones
    
    def test_tones_dict_structure(self):
        """Test TONES dict has correct structure."""
        for tone, config in ResponseGenerator.TONES.items():
            assert 'system_prompt' in config, f"{tone} missing system_prompt"
            assert 'max_length' in config, f"{tone} missing max_length"
    
    def test_default_tone(self):
        """Test default tone is 'match_style'."""
        gen = ResponseGenerator()
        assert gen.default_tone == "match_style"
    
    def test_set_tone(self):
        """Test set_tone() changes default tone."""
        gen = ResponseGenerator()
        gen.set_tone("formal")
        assert gen.default_tone == "formal"
    
    def test_get_available_tones(self):
        """Test returns list of 4 tone names."""
        gen = ResponseGenerator()
        tones = gen.get_available_tones()
        assert len(tones) == 4
        assert 'casual' in tones
        assert 'formal' in tones
        assert 'concise' in tones
        assert 'match_style' in tones
    
    def test_convenience_function_exists(self):
        """Test generate_reply() convenience function exists."""
        assert callable(generate_reply)
    
    def test_empty_email_handling(self):
        """Test graceful handling of missing email fields."""
        gen = ResponseGenerator()
        # Should not raise
        result = gen.generate_reply({})
        assert result is not None
    
    def test_generate_reply_returns_string(self):
        """Test generate_reply returns a string."""
        gen = ResponseGenerator()
        result = gen.generate_reply({'subject': 'Test', 'body_text': 'Hello'})
        assert isinstance(result, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
