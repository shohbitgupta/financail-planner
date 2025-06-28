"""
Vector database access layer.
"""
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

class VectorDatabase:
    """Vector database access for investment data retrieval."""
    
    def __init__(self, db_path: Path, collection_name: str, embedding_model: str):
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.vector_store = None
        self.retriever = None
        self.embeddings = None
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize vector database connection."""
        try:
            # Ensure database directory exists
            self.db_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize embeddings
            self.embeddings = OllamaEmbeddings(model=self.embedding_model)
            
            # Check if database exists
            if not self._database_exists():
                logger.warning(f"Vector database not found at {self.db_path}")
                logger.warning("Please run the database setup script to create the vector database")
                return False
            
            # Initialize vector store
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                persist_directory=str(self.db_path),
                embedding_function=self.embeddings
            )
            
            # Create retriever
            self.retriever = self.vector_store.as_retriever(
                search_kwargs={"k": 10}
            )
            
            self.initialized = True
            logger.info(f"Vector database initialized with collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {str(e)}")
            return False
    
    def _database_exists(self) -> bool:
        """Check if vector database exists."""
        return (self.db_path / "chroma.sqlite3").exists()
    
    def search_documents(self, query: str, k: int = 10) -> List[Document]:
        """Search for relevant documents."""
        if not self.initialized or not self.retriever:
            logger.warning("Vector database not initialized")
            return []
        
        try:
            results = self.retriever.invoke(query)
            logger.info(f"Retrieved {len(results)} documents for query: {query}")
            return results[:k]
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def search_investments(self, query: str, k: int = 10) -> List[Document]:
        """Search for relevant investment documents."""
        return self.search_documents(query, k)
    
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
    
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to vector database."""
        if not self.initialized or not self.vector_store:
            logger.error("Vector database not initialized")
            return False
        
        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Added {len(documents)} documents to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return False
    
    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from vector database."""
        if not self.initialized or not self.vector_store:
            logger.error("Vector database not initialized")
            return False
        
        try:
            self.vector_store.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents from vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return False
    
    def update_documents(self, documents: List[Document]) -> bool:
        """Update documents in vector database."""
        if not self.initialized or not self.vector_store:
            logger.error("Vector database not initialized")
            return False
        
        try:
            # For Chroma, we need to delete and re-add
            document_ids = [doc.metadata.get('id') for doc in documents if doc.metadata.get('id')]
            
            if document_ids:
                self.delete_documents(document_ids)
            
            self.add_documents(documents)
            logger.info(f"Updated {len(documents)} documents in vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error updating documents: {str(e)}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
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
                "collection_name": collection.name,
                "embedding_model": self.embedding_model
            }
            
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def check_health(self) -> bool:
        """Check if vector database is healthy."""
        if not self.initialized:
            return False
        
        try:
            # Try a simple search
            test_results = self.search_documents("test query", k=1)
            return True
        except Exception as e:
            logger.error(f"Vector database health check failed: {str(e)}")
            return False
    
    def rebuild_index(self) -> bool:
        """Rebuild vector database index."""
        if not self.initialized or not self.vector_store:
            logger.error("Vector database not initialized")
            return False
        
        try:
            # For Chroma, we can persist the database
            self.vector_store.persist()
            logger.info("Vector database index rebuilt successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {str(e)}")
            return False

# Global database instance - will be initialized by config
vector_db = None

def initialize_vector_db(db_path: Path, collection_name: str, embedding_model: str):
    """Initialize global vector database instance."""
    global vector_db
    vector_db = VectorDatabase(db_path, collection_name, embedding_model)
    return vector_db.initialize()
