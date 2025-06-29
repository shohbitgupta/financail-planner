"""
LlamaCloud RAG Service for Financial Planning
Provides cloud-deployable RAG capabilities using LlamaIndex Cloud
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from llama_index.core import VectorStoreIndex, Document, Settings
    from llama_index.core.retrievers import VectorIndexRetriever
    from llama_index.core.query_engine import RetrieverQueryEngine
    from llama_index.core.postprocessor import SimilarityPostprocessor
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.openai import OpenAIEmbedding
    LLAMAINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning(f"LlamaIndex not available: {e}")
    LLAMAINDEX_AVAILABLE = False

@dataclass
class FinancialContext:
    """Financial context retrieved from RAG system"""
    instruments: List[Dict[str, Any]]
    market_analysis: str
    risk_factors: List[str]
    recommendations: List[str]
    confidence_score: float

class LlamaCloudRAGService:
    """LlamaCloud RAG service for financial planning"""
    
    def __init__(self):
        self.initialized = False
        self.index = None
        self.query_engine = None
        self.financial_documents = []
        
    def initialize(self, api_key: str) -> bool:
        """Initialize LlamaCloud service with API key"""
        if not LLAMAINDEX_AVAILABLE:
            logger.error("LlamaIndex not available")
            return False
            
        try:
            # Set OpenAI API key for LlamaIndex
            os.environ["OPENAI_API_KEY"] = api_key
            
            # Configure LlamaIndex settings
            Settings.llm = OpenAI(model="gpt-4", temperature=0.1)
            Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
            
            logger.info("✅ LlamaCloud RAG service initialized")
            self.initialized = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LlamaCloud: {e}")
            return False
    
    def setup_financial_knowledge_base(self, financial_data: Dict[str, Any]) -> bool:
        """Setup financial knowledge base with instruments and market data"""
        if not self.initialized:
            logger.error("Service not initialized")
            return False
            
        try:
            # Convert financial data to documents
            documents = []
            
            # Add instrument documents
            for instrument in financial_data.get('instruments', []):
                doc_text = f"""
                Instrument: {instrument.get('symbol', 'N/A')}
                Name: {instrument.get('name', 'N/A')}
                Category: {instrument.get('category', 'N/A')}
                Market: {instrument.get('market', 'N/A')}
                Currency: {instrument.get('currency', 'N/A')}
                Risk Level: {instrument.get('risk_level', 'N/A')}
                Expected Return: {instrument.get('expected_return', 'N/A')}%
                Minimum Investment: {instrument.get('min_investment', 'N/A')}
                Sharia Compliant: {instrument.get('is_sharia_compliant', False)}
                Description: {instrument.get('description', 'N/A')}
                """
                
                documents.append(Document(
                    text=doc_text,
                    metadata={
                        'type': 'instrument',
                        'symbol': instrument.get('symbol'),
                        'category': instrument.get('category'),
                        'market': instrument.get('market'),
                        'risk_level': instrument.get('risk_level')
                    }
                ))
            
            # Add performance metrics documents
            for metric in financial_data.get('performance_metrics', []):
                doc_text = f"""
                Performance Data for {metric.get('symbol', 'N/A')}
                1 Year Return: {metric.get('return_1y', 'N/A')}%
                3 Year Return: {metric.get('return_3y', 'N/A')}%
                5 Year Return: {metric.get('return_5y', 'N/A')}%
                Volatility: {metric.get('volatility', 'N/A')}%
                Sharpe Ratio: {metric.get('sharpe_ratio', 'N/A')}
                Max Drawdown: {metric.get('max_drawdown', 'N/A')}%
                """
                
                documents.append(Document(
                    text=doc_text,
                    metadata={
                        'type': 'performance',
                        'symbol': metric.get('symbol')
                    }
                ))
            
            # Create vector index
            self.index = VectorStoreIndex.from_documents(documents)
            
            # Create query engine with retriever
            retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=10
            )
            
            self.query_engine = RetrieverQueryEngine(
                retriever=retriever,
                node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)]
            )
            
            self.financial_documents = documents
            logger.info(f"✅ Knowledge base setup with {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup knowledge base: {e}")
            return False
    
    def retrieve_financial_context(self, query: str, user_profile: Dict[str, Any]) -> Optional[FinancialContext]:
        """Retrieve relevant financial context for user query"""
        if not self.query_engine:
            logger.error("Query engine not initialized")
            return None
            
        try:
            # Enhance query with user profile context
            enhanced_query = f"""
            User Profile:
            - Age: {user_profile.get('age')}
            - Risk Tolerance: {user_profile.get('risk_tolerance', 'moderate')}
            - Investment Horizon: {user_profile.get('retirement_age', 65) - user_profile.get('age', 30)} years
            - Market Preference: {user_profile.get('preferred_market', 'UAE')}
            - Sharia Compliance: {user_profile.get('is_sharia_compliant', False)}
            
            Query: {query}
            
            Please provide relevant investment instruments and recommendations.
            """
            
            # Query the RAG system
            response = self.query_engine.query(enhanced_query)
            
            # Extract instruments from retrieved nodes
            instruments = []
            for node in response.source_nodes:
                if node.metadata.get('type') == 'instrument':
                    instruments.append({
                        'symbol': node.metadata.get('symbol'),
                        'category': node.metadata.get('category'),
                        'market': node.metadata.get('market'),
                        'risk_level': node.metadata.get('risk_level'),
                        'relevance_score': node.score
                    })
            
            # Generate market analysis
            market_analysis = str(response)
            
            # Extract risk factors and recommendations
            risk_factors = self._extract_risk_factors(response)
            recommendations = self._extract_recommendations(response)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(response.source_nodes)
            
            return FinancialContext(
                instruments=instruments,
                market_analysis=market_analysis,
                risk_factors=risk_factors,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"Failed to retrieve financial context: {e}")
            return None
    
    def generate_financial_plan(self, user_data: Dict[str, Any], financial_context: FinancialContext) -> str:
        """Generate comprehensive financial plan using retrieved context"""
        if not self.query_engine:
            logger.error("Query engine not initialized")
            return "RAG service not available"
            
        try:
            # Create comprehensive prompt
            prompt = f"""
            Based on the following user profile and financial context, create a comprehensive financial plan:
            
            User Profile:
            - Age: {user_data.get('age')}
            - Retirement Age: {user_data.get('retirement_age')}
            - Annual Income: {user_data.get('annual_salary')}
            - Annual Expenses: {user_data.get('annual_expenses')}
            - Current Savings: {user_data.get('current_savings')}
            - Risk Tolerance: {user_data.get('risk_tolerance')}
            - Goals: {', '.join(user_data.get('goals', []))}
            
            Available Instruments: {len(financial_context.instruments)} relevant options
            Market Analysis: {financial_context.market_analysis[:500]}...
            
            Please provide:
            1. Specific investment recommendations with allocation percentages
            2. Monthly savings targets
            3. Goal achievement timeline
            4. Risk assessment and mitigation strategies
            5. Platform recommendations for implementation
            """
            
            response = self.query_engine.query(prompt)
            return str(response)
            
        except Exception as e:
            logger.error(f"Failed to generate financial plan: {e}")
            return f"Error generating plan: {str(e)}"
    
    def _extract_risk_factors(self, response) -> List[str]:
        """Extract risk factors from RAG response"""
        # Simple extraction - could be enhanced with NLP
        risk_keywords = ['risk', 'volatility', 'uncertainty', 'market risk', 'credit risk']
        risk_factors = []
        
        response_text = str(response).lower()
        for keyword in risk_keywords:
            if keyword in response_text:
                risk_factors.append(f"Consider {keyword} in investment decisions")
        
        return risk_factors[:3]  # Limit to top 3
    
    def _extract_recommendations(self, response) -> List[str]:
        """Extract recommendations from RAG response"""
        # Simple extraction - could be enhanced with NLP
        recommendations = []
        response_text = str(response)
        
        # Look for recommendation patterns
        if "diversify" in response_text.lower():
            recommendations.append("Diversify across multiple asset classes")
        if "emergency fund" in response_text.lower():
            recommendations.append("Maintain adequate emergency fund")
        if "regular investment" in response_text.lower():
            recommendations.append("Consider systematic investment plans")
        
        return recommendations
    
    def _calculate_confidence_score(self, source_nodes) -> float:
        """Calculate confidence score based on retrieval quality"""
        if not source_nodes:
            return 0.0
        
        # Average similarity scores
        scores = [node.score for node in source_nodes if hasattr(node, 'score')]
        return sum(scores) / len(scores) if scores else 0.5
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            'service': 'LlamaCloud RAG',
            'initialized': self.initialized,
            'available': LLAMAINDEX_AVAILABLE,
            'documents_loaded': len(self.financial_documents),
            'query_engine_ready': self.query_engine is not None,
            'timestamp': datetime.now().isoformat()
        }

# Global service instance
llamacloud_rag_service = LlamaCloudRAGService()

def initialize_llamacloud_service(api_key: str) -> bool:
    """Initialize the global LlamaCloud service"""
    return llamacloud_rag_service.initialize(api_key)
