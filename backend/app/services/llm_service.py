"""
LLM service for generating financial planning responses.
"""
import logging
from typing import Dict, Any

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM operations using Ollama."""
    
    def __init__(self):
        self.llm = None
        self.initialized = False
        self.model_name = None
    
    def initialize(self, model_name: str, base_url: str = "http://localhost:11434"):
        """Initialize LLM connection."""
        try:
            self.model_name = model_name
            self.llm = OllamaLLM(
                model=model_name,
                base_url=base_url,
                temperature=0.7
            )
            
            # Test connection
            test_response = self.llm.invoke("Hello")
            if test_response:
                self.initialized = True
                logger.info(f"LLM service initialized with model: {model_name}")
                return True
            else:
                logger.error("LLM test failed - no response")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {str(e)}")
            return False
    
    def generate_financial_plan(self, user_profile, investment_context: str = "") -> str:
        """Generate financial planning response."""
        if not self.initialized:
            raise RuntimeError("LLM service not initialized")
        
        try:
            # Create prompt template
            prompt_template = PromptTemplate(
                input_variables=["user_data", "investment_context"],
                template=self._get_financial_planning_template()
            )
            
            # Format user data
            user_data_str = self._format_user_data(user_profile)
            
            # Generate prompt
            prompt = prompt_template.format(
                user_data=user_data_str,
                investment_context=investment_context
            )
            
            # Generate response
            response = self.llm.invoke(prompt)
            logger.info("Financial plan generated successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error generating financial plan: {str(e)}")
            raise
    
    def _get_financial_planning_template(self) -> str:
        """Get the financial planning prompt template."""
        return """
You are a professional financial advisor specializing in personalized investment planning. 
Create a comprehensive financial plan based on the user's profile and available investment options.

USER PROFILE:
{user_data}

AVAILABLE INVESTMENT CONTEXT:
{investment_context}

Please provide a detailed financial plan with the following sections:

**EXECUTIVE SUMMARY**
Brief overview of the user's financial situation and recommended strategy.

**PORTFOLIO RECOMMENDATIONS**
Specific investment allocations with percentages and rationale for each recommendation.
Include specific instrument names, expected returns, and risk levels.

**RISK ASSESSMENT**
Analysis of the portfolio's risk level and alignment with user's risk tolerance.

**TIME HORIZON ANALYSIS**
How the investment timeline affects the strategy and expected outcomes.

**MONTHLY SAVINGS NEEDED**
Calculate the required monthly savings to meet retirement goals.

**GOAL ACHIEVEMENT TIMELINE**
Timeline for achieving financial goals with milestones.

**ADDITIONAL ADVICE**
Additional recommendations for insurance, emergency funds, debt management, etc.

**COMPLIANCE NOTES**
Any relevant compliance considerations (Sharia, ESG, regulatory).

Focus on actionable, specific recommendations with clear rationale.
Use the investment context to recommend specific instruments when available.
Ensure all recommendations align with the user's risk tolerance and compliance requirements.
"""
    
    def _format_user_data(self, user_profile) -> str:
        """Format user profile data for the prompt."""
        return f"""
Age: {user_profile.age}
Retirement Age: {user_profile.retirement_age}
Annual Salary: ${user_profile.annual_salary:,.2f}
Annual Expenses: ${user_profile.annual_expenses:,.2f}
Current Savings: ${user_profile.current_savings:,.2f}
Risk Tolerance: {user_profile.risk_tolerance}
Investment Goals: {', '.join(user_profile.goals)}
Preferred Market: {user_profile.preferred_market}
Sharia Compliant: {'Yes' if user_profile.is_sharia_compliant else 'No'}
Investment Horizon: {user_profile.investment_horizon} years
Monthly Savings Capacity: ${user_profile.get_monthly_savings_capacity():,.2f}
Savings Rate: {user_profile.get_savings_rate():.1%}
"""
    
    def check_health(self) -> bool:
        """Check if LLM service is healthy."""
        if not self.initialized:
            return False
        
        try:
            # Simple health check
            response = self.llm.invoke("Hello")
            return bool(response and len(response.strip()) > 0)
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "model_name": self.model_name,
            "initialized": self.initialized,
            "available": self.check_health()
        }

# Global service instance
llm_service = LLMService()

def initialize(model_name: str, base_url: str):
    """Initialize the global LLM service instance."""
    global llm_service
    return llm_service.initialize(model_name, base_url)
