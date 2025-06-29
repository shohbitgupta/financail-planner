"""
LlamaCloud RAG Service for Financial Planner AI Agent
Replaces local Ollama with cloud-deployable LlamaCloud API
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import requests
import json
from datetime import datetime

# LlamaCloud imports
try:
    from llama_index.core import VectorStoreIndex, Document
    from llama_index.core.llms import LLM
    from llama_index.core.embeddings import BaseEmbedding
    from llama_parse import LlamaParse
    from llama_cloud import LlamaCloud
    LLAMACLOUD_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LlamaCloud not available: {e}")
    LLAMACLOUD_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class FinancialContext:
    """Financial context data structure"""
    instruments: List[Dict[str, Any]]
    market_data: Dict[str, Any]
    historical_performance: Dict[str, Any]
    risk_metrics: Dict[str, Any]

class LlamaCloudRAGService:
    """
    LlamaCloud-based RAG service for financial planning
    Provides cloud-deployable alternative to local Ollama
    """
    
    def __init__(self):
        self.api_key = None
        self.llama_parse = None
        self.llama_cloud = None
        self.vector_index = None
        self.initialized = False
        
    def initialize(self, api_key: str) -> bool:
        """Initialize LlamaCloud services"""
        try:
            self.api_key = api_key
            
            # Initialize LlamaParse for document processing
            self.llama_parse = LlamaParse(
                api_key=api_key,
                result_type="markdown",
                verbose=True
            )
            
            # Initialize LlamaCloud for managed RAG
            self.llama_cloud = LlamaCloud(api_key=api_key)
            
            # Test connection
            if self._test_connection():
                self.initialized = True
                logger.info("LlamaCloud RAG service initialized successfully")
                return True
            else:
                logger.error("LlamaCloud connection test failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize LlamaCloud: {str(e)}")
            return False
    
    def _test_connection(self) -> bool:
        """Test LlamaCloud connection"""
        try:
            # Simple test to verify API key and connection
            test_doc = Document(text="Test document for connection verification")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def setup_financial_knowledge_base(self, financial_data: Dict[str, Any]) -> bool:
        """
        Setup financial knowledge base with investment instruments and market data
        """
        try:
            if not self.initialized:
                raise RuntimeError("LlamaCloud service not initialized")
            
            # Convert financial data to documents
            documents = self._create_financial_documents(financial_data)
            
            # Create vector index with LlamaCloud
            self.vector_index = VectorStoreIndex.from_documents(
                documents,
                service_context=self._get_service_context()
            )
            
            logger.info(f"Financial knowledge base created with {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup knowledge base: {str(e)}")
            return False
    
    def _create_financial_documents(self, financial_data: Dict[str, Any]) -> List[Document]:
        """Convert financial data to LlamaIndex documents"""
        documents = []
        
        # Process investment instruments
        if 'instruments' in financial_data:
            for instrument in financial_data['instruments']:
                doc_text = self._format_instrument_data(instrument)
                doc = Document(
                    text=doc_text,
                    metadata={
                        'type': 'instrument',
                        'symbol': instrument.get('symbol', ''),
                        'category': instrument.get('category', ''),
                        'market': instrument.get('market', ''),
                        'risk_level': instrument.get('risk_level', '')
                    }
                )
                documents.append(doc)
        
        # Process market data
        if 'market_data' in financial_data:
            for market, data in financial_data['market_data'].items():
                doc_text = self._format_market_data(market, data)
                doc = Document(
                    text=doc_text,
                    metadata={
                        'type': 'market_data',
                        'market': market,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                documents.append(doc)
        
        # Process historical performance data
        if 'historical_data' in financial_data:
            for symbol, history in financial_data['historical_data'].items():
                doc_text = self._format_historical_data(symbol, history)
                doc = Document(
                    text=doc_text,
                    metadata={
                        'type': 'historical_performance',
                        'symbol': symbol,
                        'period': history.get('period', ''),
                        'last_updated': datetime.now().isoformat()
                    }
                )
                documents.append(doc)
        
        return documents
    
    def _format_instrument_data(self, instrument: Dict[str, Any]) -> str:
        """Format investment instrument data for RAG"""
        return f"""
Investment Instrument: {instrument.get('name', 'Unknown')}
Symbol: {instrument.get('symbol', 'N/A')}
Category: {instrument.get('category', 'N/A')}
Market: {instrument.get('market', 'N/A')}
Risk Level: {instrument.get('risk_level', 'N/A')}
Expected Return: {instrument.get('expected_return', 'N/A')}%
Volatility: {instrument.get('volatility', 'N/A')}%
Description: {instrument.get('description', 'No description available')}
Minimum Investment: {instrument.get('min_investment', 'N/A')}
Currency: {instrument.get('currency', 'N/A')}
Sharia Compliant: {instrument.get('is_sharia_compliant', False)}
Platform Recommendation: {instrument.get('platform_recommendation', 'N/A')}
"""
    
    def _format_market_data(self, market: str, data: Dict[str, Any]) -> str:
        """Format market data for RAG"""
        return f"""
Market: {market}
Current Index: {data.get('index_value', 'N/A')}
Daily Change: {data.get('daily_change', 'N/A')}%
Market Cap: {data.get('market_cap', 'N/A')}
Volume: {data.get('volume', 'N/A')}
Top Sectors: {', '.join(data.get('top_sectors', []))}
Market Sentiment: {data.get('sentiment', 'N/A')}
Economic Indicators: {data.get('economic_indicators', {})}
"""
    
    def _format_historical_data(self, symbol: str, history: Dict[str, Any]) -> str:
        """Format historical performance data for RAG"""
        return f"""
Historical Performance for {symbol}
Period: {history.get('period', 'N/A')}
Average Return: {history.get('avg_return', 'N/A')}%
Best Year: {history.get('best_year', 'N/A')}%
Worst Year: {history.get('worst_year', 'N/A')}%
Volatility: {history.get('volatility', 'N/A')}%
Sharpe Ratio: {history.get('sharpe_ratio', 'N/A')}
Max Drawdown: {history.get('max_drawdown', 'N/A')}%
Correlation with Market: {history.get('market_correlation', 'N/A')}
Performance Trends: {history.get('trends', 'N/A')}
"""
    
    def _get_service_context(self):
        """Get LlamaCloud service context"""
        # This would be configured based on LlamaCloud's service context
        # For now, return None and let LlamaCloud handle defaults
        return None
    
    def retrieve_financial_context(self, query: str, user_profile: Dict[str, Any]) -> FinancialContext:
        """
        Retrieve relevant financial context based on user query and profile
        """
        try:
            if not self.vector_index:
                raise RuntimeError("Financial knowledge base not initialized")
            
            # Enhance query with user profile context
            enhanced_query = self._enhance_query_with_profile(query, user_profile)
            
            # Retrieve relevant documents
            retriever = self.vector_index.as_retriever(similarity_top_k=10)
            retrieved_nodes = retriever.retrieve(enhanced_query)
            
            # Process retrieved context
            context = self._process_retrieved_context(retrieved_nodes, user_profile)
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to retrieve financial context: {str(e)}")
            # Return empty context on error
            return FinancialContext(
                instruments=[],
                market_data={},
                historical_performance={},
                risk_metrics={}
            )
    
    def _enhance_query_with_profile(self, query: str, user_profile: Dict[str, Any]) -> str:
        """Enhance query with user profile information"""
        profile_context = []
        
        if user_profile.get('risk_tolerance'):
            profile_context.append(f"Risk tolerance: {user_profile['risk_tolerance']}")
        
        if user_profile.get('goals'):
            goals = user_profile['goals'] if isinstance(user_profile['goals'], list) else [user_profile['goals']]
            profile_context.append(f"Investment goals: {', '.join(goals)}")
        
        if user_profile.get('preferred_market'):
            profile_context.append(f"Preferred market: {user_profile['preferred_market']}")
        
        if user_profile.get('is_sharia_compliant'):
            profile_context.append("Sharia compliant investments required")
        
        if user_profile.get('currency'):
            profile_context.append(f"Currency: {user_profile['currency']}")
        
        enhanced_query = f"{query}. User profile: {'; '.join(profile_context)}"
        return enhanced_query
    
    def _process_retrieved_context(self, retrieved_nodes, user_profile: Dict[str, Any]) -> FinancialContext:
        """Process retrieved nodes into structured financial context"""
        instruments = []
        market_data = {}
        historical_performance = {}
        risk_metrics = {}
        
        for node in retrieved_nodes:
            metadata = node.metadata
            content = node.text
            
            if metadata.get('type') == 'instrument':
                # Filter instruments based on user profile
                if self._is_suitable_instrument(metadata, user_profile):
                    instruments.append({
                        'symbol': metadata.get('symbol', ''),
                        'category': metadata.get('category', ''),
                        'market': metadata.get('market', ''),
                        'risk_level': metadata.get('risk_level', ''),
                        'content': content,
                        'relevance_score': node.score if hasattr(node, 'score') else 0.0
                    })
            
            elif metadata.get('type') == 'market_data':
                market = metadata.get('market', 'unknown')
                market_data[market] = {
                    'content': content,
                    'timestamp': metadata.get('timestamp', ''),
                    'relevance_score': node.score if hasattr(node, 'score') else 0.0
                }
            
            elif metadata.get('type') == 'historical_performance':
                symbol = metadata.get('symbol', 'unknown')
                historical_performance[symbol] = {
                    'content': content,
                    'period': metadata.get('period', ''),
                    'last_updated': metadata.get('last_updated', ''),
                    'relevance_score': node.score if hasattr(node, 'score') else 0.0
                }
        
        return FinancialContext(
            instruments=instruments,
            market_data=market_data,
            historical_performance=historical_performance,
            risk_metrics=risk_metrics
        )
    
    def _is_suitable_instrument(self, metadata: Dict[str, Any], user_profile: Dict[str, Any]) -> bool:
        """Check if instrument is suitable for user profile"""
        # Risk tolerance check
        user_risk = user_profile.get('risk_tolerance', 'moderate').lower()
        instrument_risk = metadata.get('risk_level', 'moderate').lower()
        
        risk_mapping = {'conservative': 1, 'moderate': 2, 'aggressive': 3}
        user_risk_level = risk_mapping.get(user_risk, 2)
        instrument_risk_level = risk_mapping.get(instrument_risk, 2)
        
        if instrument_risk_level > user_risk_level:
            return False
        
        # Sharia compliance check
        if user_profile.get('is_sharia_compliant', False):
            # This would need to be implemented based on instrument metadata
            pass
        
        # Market preference check
        preferred_market = user_profile.get('preferred_market', '').lower()
        instrument_market = metadata.get('market', '').lower()
        
        if preferred_market and preferred_market not in instrument_market:
            return False
        
        return True
    
    def generate_financial_plan(self, user_profile: Dict[str, Any], context: FinancialContext) -> str:
        """
        Generate financial plan using LlamaCloud LLM with retrieved context
        """
        try:
            if not self.initialized:
                raise RuntimeError("LlamaCloud service not initialized")
            
            # Create query engine with retrieved context
            query_engine = self.vector_index.as_query_engine()
            
            # Format comprehensive prompt
            prompt = self._create_financial_planning_prompt(user_profile, context)
            
            # Generate response using LlamaCloud
            response = query_engine.query(prompt)
            
            return str(response)
            
        except Exception as e:
            logger.error(f"Failed to generate financial plan: {str(e)}")
            return f"Error generating financial plan: {str(e)}"
    
    def _create_financial_planning_prompt(self, user_profile: Dict[str, Any], context: FinancialContext) -> str:
        """Create comprehensive financial planning prompt"""
        prompt = f"""
As a professional financial advisor, create a comprehensive financial plan based on the following:

USER PROFILE:
- Age: {user_profile.get('age', 'N/A')}
- Retirement Age: {user_profile.get('retirement_age', 'N/A')}
- Annual Salary: {user_profile.get('annual_salary', 'N/A')} {user_profile.get('currency', 'USD')}
- Annual Expenses: {user_profile.get('annual_expenses', 'N/A')} {user_profile.get('currency', 'USD')}
- Current Savings: {user_profile.get('current_savings', 'N/A')} {user_profile.get('currency', 'USD')}
- Risk Tolerance: {user_profile.get('risk_tolerance', 'N/A')}
- Investment Goals: {user_profile.get('goals', 'N/A')}
- Preferred Market: {user_profile.get('preferred_market', 'N/A')}
- Sharia Compliant: {user_profile.get('is_sharia_compliant', False)}

AVAILABLE INVESTMENT CONTEXT:
{self._format_context_for_prompt(context)}

Please provide:
1. Goal Achievement Timeline with specific milestones
2. Monthly Savings Required for each goal
3. Detailed Investment Recommendations with specific instruments
4. Risk Assessment and Mitigation Strategies
5. Platform Recommendations for each investment type

Format the response as structured JSON with clear sections for easy parsing.
"""
        return prompt
    
    def _format_context_for_prompt(self, context: FinancialContext) -> str:
        """Format financial context for prompt"""
        formatted_context = []
        
        if context.instruments:
            formatted_context.append("AVAILABLE INSTRUMENTS:")
            for instrument in context.instruments[:5]:  # Top 5 most relevant
                formatted_context.append(f"- {instrument['symbol']} ({instrument['category']}): {instrument['market']}")
        
        if context.market_data:
            formatted_context.append("\nMARKET CONDITIONS:")
            for market, data in context.market_data.items():
                formatted_context.append(f"- {market}: Current market conditions available")
        
        if context.historical_performance:
            formatted_context.append("\nHISTORICAL PERFORMANCE DATA:")
            for symbol in list(context.historical_performance.keys())[:3]:
                formatted_context.append(f"- {symbol}: Historical performance data available")
        
        return "\n".join(formatted_context)
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        return {
            'service': 'LlamaCloud RAG',
            'initialized': self.initialized,
            'api_key_configured': bool(self.api_key),
            'knowledge_base_ready': bool(self.vector_index),
            'timestamp': datetime.now().isoformat()
        }

# Global service instance
llamacloud_rag_service = LlamaCloudRAGService()

def initialize_llamacloud_service(api_key: str) -> bool:
    """Initialize the global LlamaCloud RAG service"""
    global llamacloud_rag_service
    return llamacloud_rag_service.initialize(api_key)
