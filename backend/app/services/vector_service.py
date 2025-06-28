"""
Vector database service for investment data retrieval.
"""
import logging
from typing import List, Optional
from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# Global service instance
vector_service = None

class VectorService:
    """Service for vector database operations."""
    
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self.embeddings = None
        self.initialized = False
    
    def initialize(self, db_path: Path, collection_name: str, embedding_model: str):
        """Initialize vector database connection."""
        try:
            # Ensure database directory exists
            db_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize embeddings
            self.embeddings = OllamaEmbeddings(model=embedding_model)
            
            # Check if database exists
            if not self._database_exists(db_path):
                logger.warning(f"Vector database not found at {db_path}")
                logger.warning("Please run the database setup script to create the vector database")
                return False
            
            # Initialize vector store
            self.vector_store = Chroma(
                collection_name=collection_name,
                persist_directory=str(db_path),
                embedding_function=self.embeddings
            )
            
            # Create retriever
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 10}
            )
            
            self.initialized = True
            logger.info(f"Vector service initialized with collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vector service: {str(e)}")
            return False
    
    def _database_exists(self, db_path: Path) -> bool:
        """Check if vector database exists."""
        return (db_path / "chroma.sqlite3").exists()
    
    def search_investments(self, query: str, k: int = 10) -> List[Document]:
        """Search for relevant investment documents."""
        if not self.initialized or not self.retriever:
            logger.warning("Vector service not initialized")
            return []
        
        try:
            results = self.retriever.invoke(query)
            logger.info(f"Retrieved {len(results)} documents for query: {query}")
            return results[:k]
            
        except Exception as e:
            logger.error(f"Error searching investments: {str(e)}")
            return []
    
    def get_contextual_recommendations(self, user_profile) -> str:
        """Get contextual investment recommendations based on user profile."""
        if not self.initialized:
            return "UAE and US market instruments available for diversified portfolio allocation"
        
        try:
            # Build query based on user profile
            goals_text = ', '.join(user_profile.goals)
            risk_text = user_profile.risk_tolerance
            market_text = user_profile.preferred_market
            sharia_text = "Sharia-compliant" if user_profile.is_sharia_compliant else ""
            
            query = f"Investment recommendations for {goals_text} with {risk_text} risk tolerance in {market_text} market {sharia_text}"
            
            # Search for relevant documents
            documents = self.search_investments(query)
            
            if documents:
                # Combine document content
                context = "\n".join([doc.page_content for doc in documents])
                logger.info(f"Generated contextual recommendations with {len(documents)} documents")
                return context
            else:
                logger.warning("No relevant documents found, using default context")
                return "UAE and US market instruments available for diversified portfolio allocation"
                
        except Exception as e:
            logger.error(f"Error generating contextual recommendations: {str(e)}")
            return "UAE and US market instruments available for diversified portfolio allocation"
    
    def check_health(self) -> bool:
        """Check if vector service is healthy."""
        if not self.initialized:
            return False
        
        try:
            # Try a simple search
            test_results = self.search_investments("test query", k=1)
            return True
        except Exception as e:
            logger.error(f"Vector service health check failed: {str(e)}")
            return False
    
    def get_collection_info(self) -> dict:
        """Get information about the vector collection."""
        if not self.initialized or not self.vector_store:
            return {"status": "not_initialized"}
        
        try:
            # Get collection stats
            collection = self.vector_store._collection
            count = collection.count()
            
            return {
                "status": "healthy",
                "document_count": count,
                "collection_name": collection.name
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {"status": "error", "error": str(e)}

# Global service instance
vector_service = VectorService()

def initialize(db_path: Path, collection_name: str, embedding_model: str):
    """Initialize the global vector service instance."""
    global vector_service
    return vector_service.initialize(db_path, collection_name, embedding_model)
