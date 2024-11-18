from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.models.chunks import Chunk, ChunkMetadata
from app.core.config import settings
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
import time
import psutil
import gc
from functools import wraps

logger = logging.getLogger(__name__)

def monitor_performance(func):
    """Decorator to monitor performance of embedding operations"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not settings.ENABLE_PERFORMANCE_MONITORING:
            return await func(*args, **kwargs)

        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            result = await func(*args, **kwargs)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            memory_used = end_memory - start_memory
            
            logger.info(
                f"Performance metrics for {func.__name__}:\n"
                f"Processing time: {end_time - start_time:.2f} seconds\n"
                f"Memory usage: {memory_used:.2f} MB"
            )

            # Check memory threshold
            if memory_used > settings.MEMORY_THRESHOLD_MB:
                logger.warning(
                    f"Memory usage ({memory_used:.2f} MB) exceeded threshold "
                    f"({settings.MEMORY_THRESHOLD_MB} MB)"
                )
                gc.collect()
            
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper

class VectorStorageService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection_name = "openapi_chunks"
        
        # Initialize model with CPU optimizations
        self.model = SentenceTransformer(
            settings.EMBEDDING_MODEL,
            device='cuda' if settings.USE_CUDA else 'cpu'
        )
        
        # Set maximum sequence length for optimization
        self.model.max_seq_length = settings.MAX_SEQUENCE_LENGTH
        
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the collection exists with proper schema"""
        # Check if collection exists using list_collections
        collections = self.client.get_collections().collections
        exists = any(collection.name == self.collection_name for collection in collections)
        
        if exists:
            logger.info(f"Collection {self.collection_name} already exists")
            return
            
        logger.info(f"Creating collection {self.collection_name}")
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=settings.VECTOR_DIMENSION,
                distance=models.Distance.COSINE
            )
        )

    def _generate_point_id(self, spec_id: str, chunk_id: str) -> int:
        """Generate a positive integer ID for a point"""
        # Use the absolute value of the hash to ensure it's positive
        # Add 1 to avoid 0 as an ID
        return abs(hash(f"{spec_id}_{chunk_id}")) + 1

    @monitor_performance
    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for a single text"""
        try:
            return self.model.encode(text, convert_to_numpy=True)
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    @monitor_performance
    async def _get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Get embeddings for a batch of texts"""
        try:
            return self.model.encode(
                texts,
                batch_size=settings.EMBEDDING_BATCH_SIZE,
                convert_to_numpy=True
            )
        except Exception as e:
            logger.error(f"Error generating embeddings batch: {str(e)}")
            raise

    @monitor_performance
    async def store_chunks(self, chunks: List[Dict[str, Any]], spec_id: str) -> None:
        """Store chunks in vector storage with batch processing"""
        try:
            logger.info(f"Storing {len(chunks)} chunks for spec {spec_id}")
            
            # Process chunks in batches
            batch_size = settings.EMBEDDING_BATCH_SIZE
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1} of {(len(chunks)-1)//batch_size + 1}")
                
                # Get text from chunks
                texts = [chunk['text'] for chunk in batch]
                
                # Get embeddings for the batch
                logger.info(f"Generating embeddings for {len(texts)} texts")
                vectors = await self._get_embeddings_batch(texts)
                
                # Create points for the batch
                points = []
                for chunk, vector in zip(batch, vectors):
                    points.append(models.PointStruct(
                        id=self._generate_point_id(spec_id, chunk['metadata']['chunk_id']),
                        vector=vector.tolist(),
                        payload={
                            "text": chunk['text'],
                            "metadata": chunk['metadata'],
                            "spec_id": spec_id
                        }
                    ))
                
                # Store the batch
                logger.info(f"Storing {len(points)} points in Qdrant")
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                
                # Force garbage collection after each batch if memory usage is high
                if psutil.Process().memory_info().rss / 1024 / 1024 > settings.MEMORY_THRESHOLD_MB:
                    gc.collect()
                
            logger.info(f"Successfully stored all chunks for spec {spec_id}")
            
        except Exception as e:
            logger.error(f"Error storing chunks: {str(e)}")
            raise

    @monitor_performance
    async def search_similar(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            # Get query embedding
            query_vector = await self._get_embedding(query)
            
            # Search in vector storage
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=limit
            )
            
            return [
                {
                    "text": result.payload["text"],
                    "metadata": result.payload["metadata"],
                    "score": result.score
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            raise

    async def search_chunks(
        self, 
        query: str, 
        spec_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for relevant chunks"""
        try:
            query_vector = await self._get_embedding(query)
            
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_vector.tolist(),
                "limit": limit
            }
            
            if spec_id:
                search_params["query_filter"] = models.Filter(
                    must=[models.FieldCondition(
                        key="spec_id",
                        match=models.MatchValue(value=spec_id)
                    )]
                )
            
            results = self.client.search(**search_params)
            return [
                {
                    "text": hit.payload["text"],
                    "metadata": hit.payload["metadata"],
                    "score": hit.score
                }
                for hit in results
            ]
        except Exception as e:
            logger.error(f"Error searching chunks: {str(e)}")
            raise

    async def delete_spec_chunks(self, spec_id: str) -> None:
        """Delete all chunks for a specific spec"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.Filter(
                    must=[models.FieldCondition(
                        key="spec_id",
                        match=models.MatchValue(value=spec_id)
                    )]
                )
            )
            logger.info(f"Deleted all chunks for spec {spec_id}")
        except Exception as e:
            logger.error(f"Error deleting chunks: {str(e)}")
            raise

    async def get_chunk_count(self, spec_id: str) -> int:
        """Get number of chunks for a specific spec"""
        try:
            result = self.client.count(
                collection_name=self.collection_name,
                count_filter=models.Filter(
                    must=[models.FieldCondition(
                        key="spec_id",
                        match=models.MatchValue(value=spec_id)
                    )]
                )
            )
            return result.count
        except Exception as e:
            logger.error(f"Error getting chunk count: {str(e)}")
            raise

    async def get_collection_size(self) -> Dict[str, float]:
        """Get the size of the vector database collection in MB.
        
        Returns:
            Dict with size breakdown:
            {
                'total': float,  # Total size in MB
                'vectors': float,  # Vector data size in MB
                'index': float,  # Index size in MB
                'metadata': float  # Metadata size in MB
            }
        """
        try:
            # Get collection info using collections API
            collection_info = self.client.get_collection(
                collection_name=self.collection_name
            )
            
            # Convert bytes to MB
            bytes_to_mb = lambda x: round(x / (1024 * 1024), 2)
            
            # Get vector config and count
            vector_size = collection_info.config.params.vectors.size
            vector_count = collection_info.vectors_count or 0
            
            # Calculate sizes
            vectors_size = bytes_to_mb(vector_size * vector_count * 4)  # 4 bytes per float
            
            # Get index size (approximation based on vector count)
            index_size = bytes_to_mb(vector_size * vector_count * 0.1)  # Index is typically ~10% of vector size
            
            # Get payload size (approximation based on vector count)
            payload_size = bytes_to_mb(vector_count * 0.5 * 1024)  # Assume average 0.5KB per vector for metadata
            
            total_size = vectors_size + index_size + payload_size
            
            # If total size is very small, return minimum values
            if total_size < 0.01:
                return {
                    'total': 0.01,
                    'vectors': 0.01,
                    'index': 0.00,
                    'metadata': 0.00
                }
            
            # Ensure optimizer_config.max_optimization_threads is a valid integer
            optimizer_config = collection_info.config.optimizer_config
            if optimizer_config.max_optimization_threads is None:
                optimizer_config.max_optimization_threads = 0
            
            # Ensure strict_mode_config does not contain extra fields
            if 'strict_mode_config' in collection_info.config:
                del collection_info.config['strict_mode_config']
            
            return {
                'total': round(total_size, 2),
                'vectors': round(vectors_size, 2),
                'index': round(index_size, 2),
                'metadata': round(payload_size, 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting collection size: {str(e)}")
            raise
