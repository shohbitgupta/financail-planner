"""
Evaluator service for improving LLM responses using Gemini.
"""
import logging
from typing import Dict, Any
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class EvaluatorService:
    """Service for evaluating and improving LLM responses."""
    
    def __init__(self):
        self.client = None
        self.model_name = None
        self.initialized = False
    
    def initialize(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """Initialize Gemini evaluator service."""
        try:
            # Import Google Generative AI
            try:
                import google.generativeai as genai
            except ImportError:
                logger.error("google-generativeai package not installed. Install with: pip install google-generativeai")
                return False

            # Configure Gemini API
            genai.configure(api_key=api_key)

            # Initialize Gemini model
            self.client = genai.GenerativeModel(model_name)
            self.model_name = model_name

            # Test connection
            test_response = self.client.generate_content("Hello")

            if test_response and test_response.text:
                self.initialized = True
                logger.info(f"Evaluator service initialized with model: {model_name}")
                return True
            else:
                logger.error("Evaluator test failed")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize evaluator service: {str(e)}")
            return False
    
    def evaluate_and_improve(self, original_response: str, user_profile) -> Dict[str, Any]:
        """Evaluate and improve the original LLM response."""
        if not self.initialized:
            logger.warning("Evaluator service not initialized, returning original response")
            return {
                "improved_response": original_response,
                "evaluation_metadata": {
                    "evaluator_used": False,
                    "reason": "Evaluator service not initialized"
                }
            }
        
        try:
            # First, evaluate the original response
            evaluation = self._evaluate_response(original_response, user_profile)
            
            # If score is below threshold, generate improved response
            threshold = 8.0
            if evaluation["overall_score"] < threshold:
                logger.info(f"Response quality score: {evaluation['overall_score']:.1f}. Generating improved response...")
                improved_response = self._generate_improved_response(original_response, evaluation, user_profile)
                
                # Evaluate the improved response
                improved_evaluation = self._evaluate_response(improved_response, user_profile)
                
                return {
                    "improved_response": improved_response,
                    "evaluation_metadata": {
                        "evaluator_used": True,
                        "original_score": evaluation["overall_score"],
                        "improved_score": improved_evaluation["overall_score"],
                        "improvement_applied": True,
                        "improvement_reason": "Score below threshold triggered improvement",
                        "threshold": threshold,
                        "original_evaluation": evaluation,
                        "improved_evaluation": improved_evaluation,
                        "evaluation_timestamp": datetime.now().isoformat()
                    }
                }
            else:
                logger.info(f"Response quality score: {evaluation['overall_score']:.1f}. No improvement needed.")
                return {
                    "improved_response": original_response,
                    "evaluation_metadata": {
                        "evaluator_used": True,
                        "original_score": evaluation["overall_score"],
                        "improvement_applied": False,
                        "improvement_reason": "Score above threshold",
                        "threshold": threshold,
                        "evaluation": evaluation,
                        "evaluation_timestamp": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in evaluation process: {str(e)}")
            return {
                "improved_response": original_response,
                "evaluation_metadata": {
                    "evaluator_used": False,
                    "error": str(e)
                }
            }
    
    def _evaluate_response(self, response: str, user_profile) -> Dict[str, Any]:
        """Evaluate the quality of a financial planning response."""
        
        evaluation_prompt = f"""
You are a financial planning expert evaluating the quality of financial advice.

USER PROFILE:
Age: {user_profile.age}, Retirement Age: {user_profile.retirement_age}
Annual Salary: ${user_profile.annual_salary:,.2f}, Annual Expenses: ${user_profile.annual_expenses:,.2f}
Current Savings: ${user_profile.current_savings:,.2f}
Risk Tolerance: {user_profile.risk_tolerance}
Goals: {', '.join(user_profile.goals)}
Preferred Market: {user_profile.preferred_market}
Sharia Compliant: {'Yes' if user_profile.is_sharia_compliant else 'No'}

FINANCIAL PLAN TO EVALUATE:
{response}

Please evaluate this financial plan on the following criteria (score 1-10 for each):

1. ACCURACY: Are the calculations and financial projections accurate?
2. COMPLETENESS: Does it cover all essential aspects of financial planning?
3. SPECIFICITY: Are the recommendations specific and actionable?
4. RISK_ALIGNMENT: Does it properly align with the user's risk tolerance?
5. MARKET_RELEVANCE: Are the recommendations relevant to the user's preferred market?
6. COMPLIANCE: Does it properly address compliance requirements (Sharia, etc.)?

Provide your evaluation in this exact JSON format:
{{
    "accuracy_score": <1-10>,
    "accuracy_feedback": "<detailed feedback>",
    "completeness_score": <1-10>,
    "completeness_feedback": "<detailed feedback>",
    "specificity_score": <1-10>,
    "specificity_feedback": "<detailed feedback>",
    "risk_alignment_score": <1-10>,
    "risk_alignment_feedback": "<detailed feedback>",
    "market_relevance_score": <1-10>,
    "market_relevance_feedback": "<detailed feedback>",
    "compliance_score": <1-10>,
    "compliance_feedback": "<detailed feedback>",
    "key_issues": ["<issue1>", "<issue2>"],
    "improvement_suggestions": ["<suggestion1>", "<suggestion2>"]
}}
"""
        
        try:
            response_obj = self.client.generate_content(
                evaluation_prompt,
                generation_config={
                    "max_output_tokens": 2000,
                    "temperature": 0.3
                }
            )

            evaluation_text = response_obj.text
            
            # Parse JSON response
            evaluation_data = json.loads(evaluation_text)
            
            # Calculate overall score
            scores = [
                evaluation_data["accuracy_score"],
                evaluation_data["completeness_score"],
                evaluation_data["specificity_score"],
                evaluation_data["risk_alignment_score"],
                evaluation_data["market_relevance_score"],
                evaluation_data["compliance_score"]
            ]
            overall_score = sum(scores) / len(scores)
            evaluation_data["overall_score"] = overall_score
            
            return evaluation_data
            
        except Exception as e:
            logger.error(f"Error evaluating response: {str(e)}")
            # Return default evaluation
            return {
                "overall_score": 7.0,
                "accuracy_score": 7,
                "completeness_score": 7,
                "specificity_score": 7,
                "risk_alignment_score": 7,
                "market_relevance_score": 7,
                "compliance_score": 7,
                "key_issues": ["Evaluation failed"],
                "improvement_suggestions": ["Manual review recommended"]
            }
    
    def _generate_improved_response(self, original_response: str, evaluation: Dict[str, Any], user_profile) -> str:
        """Generate an improved version of the response."""
        
        improvement_prompt = f"""
You are a senior financial advisor tasked with improving a financial plan.

USER PROFILE:
Age: {user_profile.age}, Retirement Age: {user_profile.retirement_age}
Annual Salary: ${user_profile.annual_salary:,.2f}, Annual Expenses: ${user_profile.annual_expenses:,.2f}
Current Savings: ${user_profile.current_savings:,.2f}
Risk Tolerance: {user_profile.risk_tolerance}
Goals: {', '.join(user_profile.goals)}
Preferred Market: {user_profile.preferred_market}
Sharia Compliant: {'Yes' if user_profile.is_sharia_compliant else 'No'}

ORIGINAL FINANCIAL PLAN:
{original_response}

EVALUATION FEEDBACK:
Key Issues: {', '.join(evaluation.get('key_issues', []))}
Improvement Suggestions: {', '.join(evaluation.get('improvement_suggestions', []))}

Please create an improved version of this financial plan that addresses the identified issues and implements the suggestions. Maintain the same structure but enhance the content quality, accuracy, and specificity.

Focus on:
- More accurate calculations and projections
- Specific investment recommendations with clear rationale
- Better risk assessment and alignment
- Enhanced compliance considerations
- More actionable advice

Provide the improved financial plan:
"""
        
        try:
            response_obj = self.client.generate_content(
                improvement_prompt,
                generation_config={
                    "max_output_tokens": 3000,
                    "temperature": 0.5
                }
            )

            improved_response = response_obj.text
            logger.info("Improved response generated successfully")
            return improved_response
            
        except Exception as e:
            logger.error(f"Error generating improved response: {str(e)}")
            return original_response
    
    def check_health(self) -> bool:
        """Check if evaluator service is healthy."""
        if not self.initialized:
            return False
        
        try:
            # Simple health check
            response = self.client.generate_content(
                "Hello",
                generation_config={"max_output_tokens": 5}
            )
            return bool(response and response.text)
        except Exception as e:
            logger.error(f"Evaluator health check failed: {str(e)}")
            return False

# Global service instance
evaluator_service = EvaluatorService()

def initialize(api_key: str, model_name: str):
    """Initialize the global evaluator service instance."""
    global evaluator_service
    return evaluator_service.initialize(api_key, model_name)
