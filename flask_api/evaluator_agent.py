"""
Financial Plan Evaluator Agent using Gemini 2.5 Pro
This agent evaluates and improves financial planning responses from Llama 3.2 LLM
"""

import json
import re
from typing import Dict, Any, Tuple
import google.generativeai as genai
from datetime import datetime

class FinancialPlanEvaluator:
    def __init__(self):
        """Initialize the evaluator with Gemini 2.5 Pro"""
        # Configure Gemini API
        api_key = "AIzaSyBAK741U0ImBRfHgsuPhKFIQrehP1j1_yU."
        # //os.getenv('GEMINI_API_KEY')
        # if not api_key:
        #     raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        
        # Initialize Gemini 2.5 Pro model
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Evaluation criteria weights
        self.evaluation_criteria = {
            'accuracy': 0.25,           # Financial calculations and data accuracy
            'completeness': 0.20,       # All required sections present
            'specificity': 0.20,        # Specific recommendations vs generic advice
            'risk_alignment': 0.15,     # Risk recommendations match user profile
            'market_relevance': 0.10,   # UAE/US market specific advice
            'compliance': 0.10          # Sharia compliance if required
        }
        
        print("Financial Plan Evaluator initialized with Gemini 2.5 Pro")

    def evaluate_financial_plan(self, llm_response: str, user_data: Dict[str, Any], 
                               financial_metrics: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
        """
        Evaluate the LLM response and return evaluation results and improved response
        
        Args:
            llm_response: Original response from Llama 3.2
            user_data: User profile data
            financial_metrics: Calculated financial metrics
            
        Returns:
            Tuple of (evaluation_results, improved_response)    
        """
        try:
            # Step 1: Evaluate the original response
            evaluation_results = self._evaluate_response_quality(llm_response, user_data, financial_metrics)
            
            # Step 2: Determine if improvement is needed
            overall_score = evaluation_results['overall_score']

            # Store original evaluation for detailed comparison
            original_evaluation = evaluation_results.copy()

            if overall_score >= 8.0:
                print(f"Response quality is excellent (score: {overall_score:.1f}). No improvement needed.")
                evaluation_results['improvement_applied'] = False
                evaluation_results['original_response'] = llm_response
                evaluation_results['final_response'] = llm_response
                evaluation_results['improvement_details'] = {
                    'reason': 'Score above threshold',
                    'threshold': 8.0,
                    'original_score': overall_score
                }
                return evaluation_results, llm_response

            print(f"Response quality score: {overall_score:.1f}. Generating improved response...")

            # Step 3: Generate improved response
            improved_response = self._generate_improved_response(
                llm_response, user_data, financial_metrics, evaluation_results
            )

            # Step 4: Re-evaluate the improved response
            final_evaluation = self._evaluate_response_quality(improved_response, user_data, financial_metrics)

            print(f"Improved response quality score: {final_evaluation['overall_score']:.1f}")
            print(f"Evaluation complete : {improved_response}")

            # Step 5: Create comprehensive evaluation details
            final_evaluation['improvement_applied'] = True
            final_evaluation['original_response'] = llm_response
            final_evaluation['final_response'] = improved_response
            final_evaluation['original_evaluation'] = original_evaluation
            final_evaluation['improvement_details'] = {
                'original_score': overall_score,
                'improved_score': final_evaluation['overall_score'],
                'score_improvement': final_evaluation['overall_score'] - overall_score,
                'threshold': 8.0,
                'improvement_reason': 'Score below threshold triggered improvement'
            }

            # Add detailed comparison
            final_evaluation['detailed_comparison'] = self._create_detailed_comparison(
                original_evaluation, final_evaluation
            )

            return final_evaluation, improved_response
            
        except Exception as e:
            print(f"Error in evaluator agent: {e}")
            # Return original response if evaluation fails
            return {
                'overall_score': 5.0,
                'evaluation_details': {'error': str(e)},
                'improvement_needed': False
            }, llm_response

    def _evaluate_response_quality(self, response: str, user_data: Dict[str, Any], 
                                 financial_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the quality of a financial planning response"""
        
        evaluation_prompt = f"""
        You are a senior financial planning expert evaluating the quality of an AI-generated financial plan.
        
        USER PROFILE:
        - Age: {user_data.get('age')}
        - Retirement Age: {user_data.get('retirement_age')}
        - Annual Income: ${user_data.get('annual_salary', 0):,.0f}
        - Annual Expenses: ${user_data.get('annual_expenses', 0):,.0f}
        - Current Savings: ${user_data.get('current_savings', 0):,.0f}
        - Risk Tolerance: {user_data.get('risk_tolerance', 'moderate')}
        - Goals: {', '.join(user_data.get('goals', []))}
        - Sharia Compliant: {user_data.get('is_sharia_compliant', False)}
        - Preferred Market: {user_data.get('preferred_market', 'UAE')}
        
        FINANCIAL METRICS:
        - Investment Horizon: {financial_metrics.get('investment_horizon', 0)} years
        - Monthly Savings Capacity: ${financial_metrics.get('monthly_savings_capacity', 0):,.0f}
        - Savings Rate: {financial_metrics.get('savings_rate', 0):.1%}
        
        FINANCIAL PLAN TO EVALUATE:
        {response}
        
        Please evaluate this financial plan on the following criteria (score 1-10 for each):
        
        1. ACCURACY (25%): Are financial calculations correct? Are return expectations realistic?
        2. COMPLETENESS (20%): Are all required sections present and well-developed?
        3. SPECIFICITY (20%): Are recommendations specific (actual stocks/bonds) vs generic?
        4. RISK_ALIGNMENT (15%): Do recommendations match the user's risk tolerance?
        5. MARKET_RELEVANCE (10%): Are UAE/US market opportunities properly addressed?
        6. COMPLIANCE (10%): If Sharia compliance required, are recommendations appropriate?
        
        Respond in this exact JSON format:
        {{
            "accuracy_score": <1-10>,
            "accuracy_feedback": "<specific feedback>",
            "completeness_score": <1-10>,
            "completeness_feedback": "<specific feedback>",
            "specificity_score": <1-10>,
            "specificity_feedback": "<specific feedback>",
            "risk_alignment_score": <1-10>,
            "risk_alignment_feedback": "<specific feedback>",
            "market_relevance_score": <1-10>,
            "market_relevance_feedback": "<specific feedback>",
            "compliance_score": <1-10>,
            "compliance_feedback": "<specific feedback>",
            "key_issues": ["<issue1>", "<issue2>", "<issue3>"],
            "improvement_suggestions": ["<suggestion1>", "<suggestion2>", "<suggestion3>"]
        }}
        """
        
        try:
            response_obj = self.model.generate_content(evaluation_prompt)
            evaluation_text = response_obj.text
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', evaluation_text, re.DOTALL)
            if json_match:
                evaluation_data = json.loads(json_match.group())
            else:
                raise ValueError("Could not extract JSON from evaluation response")
            
            # Calculate overall score
            overall_score = (
                evaluation_data['accuracy_score'] * self.evaluation_criteria['accuracy'] +
                evaluation_data['completeness_score'] * self.evaluation_criteria['completeness'] +
                evaluation_data['specificity_score'] * self.evaluation_criteria['specificity'] +
                evaluation_data['risk_alignment_score'] * self.evaluation_criteria['risk_alignment'] +
                evaluation_data['market_relevance_score'] * self.evaluation_criteria['market_relevance'] +
                evaluation_data['compliance_score'] * self.evaluation_criteria['compliance']
            )
            
            return {
                'overall_score': overall_score,
                'evaluation_details': evaluation_data,
                'improvement_needed': overall_score < 8.0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error in evaluation: {e}")
            return {
                'overall_score': 5.0,
                'evaluation_details': {'error': str(e)},
                'improvement_needed': True
            }

    def _generate_improved_response(self, original_response: str, user_data: Dict[str, Any], 
                                  financial_metrics: Dict[str, Any], evaluation: Dict[str, Any]) -> str:
        """Generate an improved financial planning response"""
        
        improvement_prompt = f"""
        You are a senior financial planning expert. You need to improve a financial plan based on evaluation feedback.
        
        USER PROFILE:
        - Age: {user_data.get('age')}
        - Retirement Age: {user_data.get('retirement_age')}
        - Annual Income: ${user_data.get('annual_salary', 0):,.0f}
        - Annual Expenses: ${user_data.get('annual_expenses', 0):,.0f}
        - Current Savings: ${user_data.get('current_savings', 0):,.0f}
        - Risk Tolerance: {user_data.get('risk_tolerance', 'moderate')}
        - Goals: {', '.join(user_data.get('goals', []))}
        - Sharia Compliant: {user_data.get('is_sharia_compliant', False)}
        - Preferred Market: {user_data.get('preferred_market', 'UAE')}

        FINANCIAL METRICS:
        - Monthly Savings Capacity: ${financial_metrics.get('monthly_savings_capacity', 0):,.0f}
        - Investment Horizon: {financial_metrics.get('investment_horizon', 0)} years
        - Additional Monthly Needed: ${financial_metrics.get('additional_monthly_needed', 0):,.0f}
        
        ORIGINAL FINANCIAL PLAN:
        {original_response}
        
        EVALUATION FEEDBACK:
        Key Issues: {evaluation['evaluation_details'].get('key_issues', [])}
        Improvement Suggestions: {evaluation['evaluation_details'].get('improvement_suggestions', [])}
        
        SPECIFIC FEEDBACK BY CATEGORY:
        - Accuracy: {evaluation['evaluation_details'].get('accuracy_feedback', '')}
        - Completeness: {evaluation['evaluation_details'].get('completeness_feedback', '')}
        - Specificity: {evaluation['evaluation_details'].get('specificity_feedback', '')}
        - Risk Alignment: {evaluation['evaluation_details'].get('risk_alignment_feedback', '')}
        - Market Relevance: {evaluation['evaluation_details'].get('market_relevance_feedback', '')}
        - Compliance: {evaluation['evaluation_details'].get('compliance_feedback', '')}
        
        Please create an IMPROVED financial plan that addresses all the feedback. The plan should include:
        
        1. EXECUTIVE SUMMARY (2-3 sentences about the overall financial situation)
        2. PORTFOLIO RECOMMENDATIONS (List 3-5 specific investments with allocation percentages)
        3. RISK ASSESSMENT (Brief analysis of portfolio risk level based on user profile)
        4. TIME HORIZON ANALYSIS (How the investment timeline affects strategy)
        5. MONTHLY SAVINGS NEEDED (Specific amount to reach retirement goals)
        6. GOAL ACHIEVEMENT TIMELINE (When each goal can be achieved)
        7. ADDITIONAL ADVICE (3-4 actionable recommendations)
        8. COMPLIANCE NOTES (If Sharia compliance is required, mention suitable instruments)
        
        Focus on:
        - Specific instrument names (Tesla, Apple, Emirates NBD, etc.) instead of generic categories
        - Being Senior Planner, please suggest the instruments for better investment
        - Accurate financial calculations
        - Risk-appropriate recommendations
        - UAE and US market opportunities
        
        Keep responses professional, specific with numbers, and actionable.
        """
        
        try:
            response_obj = self.model.generate_content(improvement_prompt)
            improved_response = response_obj.text
            
            return improved_response
            
        except Exception as e:
            print(f"Error generating improved response: {e}")
            return original_response

    def _create_detailed_comparison(self, original_eval: Dict[str, Any],
                                  final_eval: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed comparison between original and improved evaluations"""

        comparison = {
            'score_changes': {},
            'feedback_comparison': {},
            'key_improvements': [],
            'areas_enhanced': []
        }

        # Compare scores for each criteria
        criteria = ['accuracy', 'completeness', 'specificity', 'risk_alignment', 'market_relevance', 'compliance']

        for criterion in criteria:
            original_score = original_eval['evaluation_details'].get(f'{criterion}_score', 0)
            final_score = final_eval['evaluation_details'].get(f'{criterion}_score', 0)

            comparison['score_changes'][criterion] = {
                'original': original_score,
                'improved': final_score,
                'change': final_score - original_score,
                'improvement_percentage': ((final_score - original_score) / original_score * 100) if original_score > 0 else 0
            }

            # Track significant improvements
            if final_score - original_score >= 2.0:
                comparison['areas_enhanced'].append({
                    'area': criterion.replace('_', ' ').title(),
                    'improvement': final_score - original_score,
                    'original_feedback': original_eval['evaluation_details'].get(f'{criterion}_feedback', ''),
                    'improved_feedback': final_eval['evaluation_details'].get(f'{criterion}_feedback', '')
                })

        # Extract key improvements from evaluation details
        original_issues = original_eval['evaluation_details'].get('key_issues', [])
        improvement_suggestions = original_eval['evaluation_details'].get('improvement_suggestions', [])

        comparison['key_improvements'] = improvement_suggestions
        comparison['issues_addressed'] = original_issues

        return comparison

# Singleton instance
evaluator_agent = None

def get_evaluator_agent():
    """Get or create the evaluator agent instance"""
    global evaluator_agent
    if evaluator_agent is None:
        try:
            evaluator_agent = FinancialPlanEvaluator()
        except Exception as e:
            print(f"Warning: Could not initialize evaluator agent: {e}")
            evaluator_agent = None
    return evaluator_agent

def evaluate_and_improve_response(llm_response: str, user_data: Dict[str, Any], 
                                financial_metrics: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """
    Main function to evaluate and improve a financial planning response
    
    Args:
        llm_response: Original response from Llama 3.2
        user_data: User profile data
        financial_metrics: Calculated financial metrics
        
    Returns:
        Tuple of (evaluation_results, improved_response)
    """
    evaluator = get_evaluator_agent()
    
    if evaluator is None:
        print("Evaluator agent not available. Using original response.")
        return {
            'overall_score': 5.0,
            'evaluation_details': {'error': 'Evaluator not available'},
            'improvement_needed': False
        }, llm_response
    
    return evaluator.evaluate_financial_plan(llm_response, user_data, financial_metrics)
