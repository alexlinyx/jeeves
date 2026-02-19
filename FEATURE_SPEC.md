# Feature Spec: RAG Pipeline

**Phase:** 2.2  
**Branch:** `feature/2.2-rag-pipeline`  
**Priority:** P0 (Blocking)  
**Est. Time:** 20 hours

---

## Objective

Build the Retrieval-Augmented Generation pipeline to index training emails into ChromaDB and enable semantic search for context-aware response generation.

---

## Acceptance Criteria

- [ ] ChromaDB installed and working
- [ ] Embedding model downloaded (`BAAI/bge-base-en-v1.5`)
- [ ] `src/rag.py` implements RAG pipeline
- [ ] `index_emails(csv_path)` indexes training emails
- [ ] `search(query, top_k=5)` returns relevant emails
- [ ] Test: Query "refund request" → returns 5 similar past emails
- [ ] Unit tests pass

---

## Deliverable

### `src/rag.py`

```python
"""RAG pipeline for email context retrieval."""
import os
import csv
from typing import List, Dict, Optional
from datetime import datetime


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline using ChromaDB."""
    
    DEFAULT_EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
    DEFAULT_COLLECTION = "jeeves-emails"
    
    def __init__(
        self,
        persist_directory: str = "data/chroma_db",
        embedding_model: str = None,
        collection_name: str = None
    ):
        """Initialize RAG pipeline.
        
        Args:
            persist_directory: Where to store ChromaDB
            embedding_model: HuggingFace embedding model
            collection_name: ChromaDB collection name
        """
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model or os.environ.get(
            'EMBEDDING_MODEL', self.DEFAULT_EMBEDDING_MODEL
        )
        self.collection_name = collection_name or self.DEFAULT_COLLECTION
        self.client = None
        self.collection = None
        self.embedding_function = None
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB and embedding function."""
        pass
    
    def index_emails(self, csv_path: str, batch_size: int = 100) -> int:
        """Index emails from CSV into ChromaDB.
        
        Args:
            csv_path: Path to training_emails.csv
            batch_size: Number of emails to process at once
            
        Returns:
            Number of emails indexed
        """
        pass
    
    def add_email(
        self,
        text: str,
        metadata: Dict,
        email_id: str = None
    ) -> str:
        """Add a single email to the index.
        
        Args:
            text: Email body text
            metadata: Dict with thread_id, from, subject, etc.
            email_id: Optional ID (generated if not provided)
            
        Returns:
            Email ID
        """
        pass
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict = None
    ) -> List[Dict]:
        """Search for relevant emails.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of dicts with 'text', 'metadata', 'distance'
        """
        pass
    
    def search_by_topic(self, topic: str, top_k: int = 5) -> List[Dict]:
        """Search emails by topic/keyword.
        
        Args:
            topic: Topic keyword
            top_k: Number of results
            
        Returns:
            List of relevant emails
        """
        pass
    
    def get_similar_emails(
        self,
        email_text: str,
        top_k: int = 5
    ) -> List[Dict]:
        """Find emails similar to given text.
        
        Args:
            email_text: Reference email text
            top_k: Number of similar emails
            
        Returns:
            List of similar emails
        """
        pass
    
    def get_sent_emails(self, top_k: int = 10) -> List[Dict]:
        """Get user's sent emails for style matching.
        
        Args:
            top_k: Number of emails to return
            
        Returns:
            List of sent emails
        """
        pass
    
    def delete_all(self):
        """Clear all indexed emails."""
        pass
    
    def get_stats(self) -> Dict:
        """Get index statistics.
        
        Returns:
            Dict with count, model, etc.
        """
        pass
    
    def rebuild_index(self, csv_path: str) -> int:
        """Clear and rebuild index from CSV.
        
        Args:
            csv_path: Path to training_emails.csv
            
        Returns:
            Number of emails indexed
        """
        pass


# Convenience functions

def index_emails(csv_path: str, **kwargs) -> int:
    """Quick function to index emails.
    
    Args:
        csv_path: Path to training_emails.csv
        **kwargs: Additional args passed to RAGPipeline
        
    Returns:
        Number of emails indexed
    """
    rag = RAGPipeline(**kwargs)
    return rag.index_emails(csv_path)


def search(query: str, top_k: int = 5, **kwargs) -> List[Dict]:
    """Quick search function.
    
    Args:
        query: Search query
        top_k: Number of results
        **kwargs: Additional args
        
    Returns:
        List of relevant emails
    """
    rag = RAGPipeline(**kwargs)
    return rag.search(query, top_k)
```

---

## Data Flow

```
training_emails.csv
       │
       ▼
┌──────────────────┐
│  RAGPipeline    │
│  .index_emails() │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│   ChromaDB      │
│  (vector store) │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  .search()      │
│ .get_sent_email()│
└──────────────────┘
       │
       ▼
   Email Context
       │
       ▼
┌──────────────────┐
│  LLM Prompt     │
└──────────────────┘
```

---

## Tasks

### 2.2.1 Install ChromaDB (30 min)
- [ ] Install: `pip install chromadb sentence-transformers`
- [ ] Verify: `python -c "import chromadb; print(chromadb.__version__)"`

### 2.2.2 Download Embedding Model (1 hr)
- [ ] Model: `BAAI/bge-base-en-v1.5` (~400MB)
- [ ] Test: `python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('BAAI/bge-base-en-v1.5'); print(m.encode('test').shape)"`

### 2.2.3 Build RAG Pipeline (8 hrs)
- [ ] Implement RAGPipeline class
- [ ] Set up ChromaDB client with persistence
- [ ] Implement embedding function using sentence-transformers
- [ ] Implement indexing (CSV → ChromaDB)
- [ ] Implement search (query → results)
- [ ] Add metadata filtering

### 2.2.4 Implement Context Functions (4 hrs)
- [ ] `get_sent_emails()` for style matching
- [ ] `get_similar_emails()` for context
- [ ] `search_by_topic()` keyword search

### 2.2.5 Test Retrieval Quality (4 hrs)
- [ ] Test: Query "refund request" → 5 similar emails
- [ ] Test various query types
- [ ] Measure retrieval accuracy

### 2.2.6 Unit Tests (2.5 hrs)
- [ ] Test RAGPipeline initialization
- [ ] Test indexing
- [ ] Test search
- [ ] Test edge cases

---

## Dependencies

| Dependency | Purpose |
|------------|---------|
| chromadb | Vector database |
| sentence-transformers | Embedding model |
| huggingface-hub | Model downloads |

---

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `EMBEDDING_MODEL` | BAAI/bge-base-en-v1.5 | HuggingFace model |
| `CHROMA_PERSIST_DIR` | data/chroma_db | DB storage path |

---

## Testing

```bash
# Test ChromaDB import
python -c "import chromadb; print('OK')"

# Test embedding model
python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('BAAI/bge-base-en-v1.5'); print(m.encode('test').shape)"

# Index emails
python -c "
from src.rag import RAGPipeline
rag = RAGPipeline()
count = rag.index_emails('data/training_emails.csv')
print(f'Indexed {count} emails')
"

# Search
python -c "
from src.rag import RAGPipeline
rag = RAGPipeline()
results = rag.search('refund request', top_k=5)
for r in results:
    print(r['metadata']['subject'], r['distance'])
"

# Get stats
python -c "
from src.rag import RAGPipeline
print(RAGPipeline().get_stats())
"

# Run tests
pytest tests/test_rag.py -v
```

---

## Schema

### ChromaDB Collection Schema

```python
{
    "ids": ["email_1", "email_2", ...],
    "embeddings": [[vector], [vector], ...],  # 768-dim for bge-base
    "documents": ["email body text", ...],
    "metadatas": [
        {
            "thread_id": "abc123",
            "from": "sender@example.com",
            "subject": "Subject Line",
            "sent_by_you": "True",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        ...
    ]
}
```

---

## Notes

- Embedding model runs on CPU (GPU optional for speed)
- First run downloads model (~400MB)
- ChromaDB persists to disk - index survives restarts
- Index rebuilds if model changes

---

## Definition of Done

1. ChromaDB installed and working
2. Embedding model downloaded and tested
3. `src/rag.py` implements RAGPipeline
4. `index_emails(csv_path)` indexes training emails
5. `search(query, top_k)` returns relevant results
6. Test query "refund request" → 5 similar emails
7. Unit tests pass
8. Branch pushed to GitHub
9. PR created
