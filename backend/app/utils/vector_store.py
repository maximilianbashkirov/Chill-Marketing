from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
from ..config import settings


class VectorDatabase:
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = 768  # Default for most embedding models
        
    def initialize_collection(self):
        """Initialize Qdrant collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Collection '{self.collection_name}' created successfully")
            else:
                print(f"Collection '{self.collection_name}' already exists")
        except Exception as e:
            print(f"Error initializing collection: {e}")
    
    def add_vector(self, vector: List[float], payload: Dict[str, Any], vector_id: Optional[str] = None) -> str:
        """Add a vector to the collection"""
        if vector_id is None:
            vector_id = str(len(self.client.scroll(self.collection_name)[0]) + 1)
        
        point = PointStruct(
            id=int(vector_id) if vector_id.isdigit() else hash(vector_id) % 1000000,
            vector=vector,
            payload=payload
        )
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )
        
        return vector_id
    
    def search_similar(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar vectors"""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            }
            for result in results
        ]
    
    def delete_vector(self, vector_id: str):
        """Delete a vector from the collection"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector={"points": [int(vector_id) if vector_id.isdigit() else hash(vector_id) % 1000000]}
        )
    
    def get_all_vectors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all vectors from the collection"""
        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            limit=limit
        )
        
        return [
            {
                "id": result.id,
                "payload": result.payload,
                "vector": result.vector if hasattr(result, 'vector') else None
            }
            for result in results
        ]


# Singleton instance
vector_db = VectorDatabase()
