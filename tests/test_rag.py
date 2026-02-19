"""Tests for RAG pipeline."""
import pytest
import os
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/jeeves')

from src.rag import RAGPipeline, index_emails, search


class TestRAGPipeline:
    """Test cases for RAGPipeline."""
    
    def test_rag_file_exists(self):
        """Test rag.py exists."""
        assert os.path.exists('/home/ubuntu/.openclaw/workspace/jeeves/src/rag.py')
    
    def test_rag_import(self):
        """Test RAGPipeline can be imported."""
        from src.rag import RAGPipeline
        assert RAGPipeline is not None
    
    def test_class_has_required_methods(self):
        """Test RAGPipeline has all required methods."""
        from src.rag import RAGPipeline
        required = ['index_emails', 'search', 'get_sent_emails', 
                    'get_similar_emails', 'get_stats', 'delete_all', 'rebuild_index']
        for method in required:
            assert hasattr(RAGPipeline, method), f"Missing method: {method}"
    
    def test_index_emails_function_exists(self):
        """Test convenience function exists."""
        assert callable(index_emails)
    
    def test_search_function_exists(self):
        """Test search function exists."""
        assert callable(search)
    
    def test_default_model(self):
        """Test default embedding model is set."""
        from src.rag import RAGPipeline
        assert RAGPipeline.DEFAULT_EMBEDDING_MODEL == "BAAI/bge-base-en-v1.5"
    
    def test_default_collection(self):
        """Test default collection name."""
        from src.rag import RAGPipeline
        assert RAGPipeline.DEFAULT_COLLECTION == "jeeves-emails"
    
    def test_requirements_have_dependencies(self):
        """Test requirements.txt has chromadb."""
        with open('/home/ubuntu/.openclaw/workspace/jeeves/requirements.txt', 'r') as f:
            content = f.read()
        assert 'chromadb' in content
        assert 'sentence-transformers' in content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])