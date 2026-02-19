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
        """Initialize RAG pipeline."""
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
        import chromadb
        from sentence_transformers import SentenceTransformer
        
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Load embedding model
        self.embedding_function = SentenceTransformer(self.embedding_model)
    
    def _embed(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        embeddings = self.embedding_function.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def index_emails(self, csv_path: str, batch_size: int = 100) -> int:
        """Index emails from CSV into ChromaDB."""
        import chromadb
        
        count = 0
        batch_ids = []
        batch_docs = []
        batch_metadatas = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                email_id = f"email_{i}"
                batch_ids.append(email_id)
                batch_docs.append(row.get('body_text', ''))
                batch_metadatas.append({
                    'thread_id': row.get('thread_id', ''),
                    'from': row.get('from', ''),
                    'subject': row.get('subject', ''),
                    'sent_by_you': row.get('sent_by_you', 'False'),
                    'timestamp': row.get('timestamp', '')
                })
                
                if len(batch_ids) >= batch_size:
                    embeddings = self._embed(batch_docs)
                    self.collection.upsert(
                        ids=batch_ids,
                        documents=batch_docs,
                        metadatas=batch_metadatas,
                        embeddings=embeddings
                    )
                    count += len(batch_ids)
                    batch_ids = []
                    batch_docs = []
                    batch_metadatas = []
        
        # Handle remaining
        if batch_ids:
            embeddings = self._embed(batch_docs)
            self.collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_metadatas,
                embeddings=embeddings
            )
            count += len(batch_ids)
        
        return count
    
    def add_email(self, text: str, metadata: Dict, email_id: str = None) -> str:
        """Add a single email to the index."""
        if email_id is None:
            email_id = f"email_{self.collection.count()}"
        
        embedding = self._embed([text])[0]
        self.collection.upsert(
            ids=[email_id],
            documents=[text],
            metadatas=[metadata],
            embeddings=[embedding]
        )
        return email_id
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Dict = None
    ) -> List[Dict]:
        """Search for relevant emails."""
        query_embedding = self._embed([query])[0]
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        output = []
        for i in range(len(results['ids'][0])):
            output.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        return output
    
    def search_by_topic(self, topic: str, top_k: int = 5) -> List[Dict]:
        """Search emails by topic/keyword."""
        return self.search(topic, top_k)
    
    def get_similar_emails(self, email_text: str, top_k: int = 5) -> List[Dict]:
        """Find emails similar to given text."""
        return self.search(email_text, top_k)
    
    def get_sent_emails(self, top_k: int = 10) -> List[Dict]:
        """Get user's sent emails for style matching."""
        return self.search("", top_k, filter_metadata={'sent_by_you': 'True'})
    
    def delete_all(self):
        """Clear all indexed emails."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_stats(self) -> Dict:
        """Get index statistics."""
        return {
            'count': self.collection.count(),
            'collection_name': self.collection_name,
            'embedding_model': self.embedding_model,
            'persist_directory': self.persist_directory
        }
    
    def rebuild_index(self, csv_path: str) -> int:
        """Clear and rebuild index from CSV."""
        self.delete_all()
        return self.index_emails(csv_path)


# Convenience functions

def index_emails(csv_path: str, **kwargs) -> int:
    """Quick function to index emails."""
    rag = RAGPipeline(**kwargs)
    return rag.index_emails(csv_path)


def search(query: str, top_k: int = 5, **kwargs) -> List[Dict]:
    """Quick search function."""
    rag = RAGPipeline(**kwargs)
    return rag.search(query, top_k)
