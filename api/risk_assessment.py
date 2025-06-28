import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class RiskCategory(Enum):
    CONSERVATIVE = "Conservative"
    MODERATE_CONSERVATIVE = "Moderate Conservative"
    MODERATE = "Moderate"
    MODERATE_AGGRESSIVE = "Moderate Aggressive"
    AGGRESSIVE = "Aggressive"

@dataclass
class RiskQuestion:
    """Individual risk assessment question"""
    question: str
    options: List[str]
    scores: List[int]  # Risk scores for each option (1-10 scale)
    weight: float = 1.0  # Question importance weight

@dataclass
class RiskProfile:
    """Complete risk assessment profile"""
    risk_score: int  # 1-10 scale
    risk_category: RiskCategory
    time_horizon: int  # years
    financial_capacity: str  # High, Medium, Low
    behavioral_traits: Dict[str, str]
    recommendations: List[str]

class RiskAssessment:
    """Sophisticated risk profiling system"""
    
    def __init__(self):
        self.questions = self._initialize_questions()
        
    def _initialize_questions(self) -> List[RiskQuestion]:
        """Initialize comprehensive risk assessment questions"""
        
        questions = [
            RiskQuestion(
                question="What is your primary investment objective?",
                options=[
                    "Capital preservation - I want to protect my money",
                    "Income generation - I want steady returns",
                    "Balanced growth - I want moderate growth with some income",
                    "Capital growth - I want my money to grow significantly",
                    "Aggressive growth - I want maximum growth potential"
                ],
                scores=[1, 3, 5, 7, 10],
                weight=2.0
            ),
            
            RiskQuestion(
                question="How would you react if your investment portfolio lost 20% in a year?",
                options=[
                    "I would panic and sell everything immediately",
                    "I would be very concerned and consider selling",
                    "I would be worried but hold on",
                    "I would be disappointed but stay invested",
                    "I would see it as a buying opportunity"
                ],
                scores=[1, 3, 5, 7, 10],
                weight=2.5
            ),
            
            RiskQuestion(
                question="What is your investment time horizon?",
                options=[
                    "Less than 2 years",
                    "2-5 years", 
                    "5-10 years",
                    "10-20 years",
                    "More than 20 years"
                ],
                scores=[1, 3, 5, 8, 10],
                weight=2.0
            ),
            
            RiskQuestion(
                question="How much investment experience do you have?",
                options=[
                    "No experience - I'm a complete beginner",
                    "Limited experience - I've made a few investments",
                    "Some experience - I understand basic concepts",
                    "Good experience - I actively manage investments",
                    "Extensive experience - I'm very knowledgeable"
                ],
                scores=[2, 4, 5, 7, 9],
                weight=1.5
            ),
            
            RiskQuestion(
                question="What percentage of your total wealth are you planning to invest?",
                options=[
                    "Less than 10%",
                    "10-25%",
                    "25-50%",
                    "50-75%",
                    "More than 75%"
                ],
                scores=[8, 6, 5, 3, 1],
                weight=1.8
            ),
            
            RiskQuestion(
                question="How stable is your income?",
                options=[
                    "Very unstable - irregular income",
                    "Somewhat unstable - variable income",
                    "Moderately stable - mostly predictable",
                    "Stable - regular salary",
                    "Very stable - guaranteed income"
                ],
                scores=[2, 4, 6, 8, 10],
                weight=1.5
            ),
            
            RiskQuestion(
                question="Do you have an emergency fund covering 6+ months of expenses?",
                options=[
                    "No emergency fund",
                    "Less than 3 months covered",
                    "3-6 months covered",
                    "6-12 months covered",
                    "More than 12 months covered"
                ],
                scores=[2, 4, 6, 8, 10],
                weight=1.5
            ),
            
            RiskQuestion(
                question="Which statement best describes your attitude toward risk?",
                options=[
                    "I avoid risk whenever possible",
                    "I'm willing to take small risks for small gains",
                    "I'm comfortable with moderate risk for moderate gains",
                    "I'm willing to take significant risks for higher returns",
                    "I actively seek high-risk, high-reward opportunities"
                ],
                scores=[1, 3, 5, 8, 10],
                weight=2.0
            ),
            
            RiskQuestion(
                question="How often do you plan to monitor your investments?",
                options=[
                    "Daily - I want to track every movement",
                    "Weekly - I like to stay informed",
                    "Monthly - Regular check-ins",
                    "Quarterly - Periodic reviews",
                    "Annually - Long-term perspective"
                ],
                scores=[3, 4, 6, 8, 10],
                weight=1.0
            ),
            
            RiskQuestion(
                question="If you had $10,000 to invest, which option would you choose?",
                options=[
                    "Government bonds with 3% guaranteed return",
                    "Bank deposits with 4% return",
                    "Balanced mutual fund with 6-8% expected return",
                    "Growth stocks with 8-12% expected return",
                    "High-growth tech stocks with 15%+ potential"
                ],
                scores=[1, 2, 5, 8, 10],
                weight=2.0
            )
        ]
        
        return questions
    
    def conduct_assessment(self) -> RiskProfile:
        """Conduct interactive risk assessment"""
        
        print("\n" + "="*60)
        print("🎯 COMPREHENSIVE RISK ASSESSMENT")
        print("="*60)
        print("This assessment will help determine your optimal investment strategy.")
        print("Please answer all questions honestly for the best recommendations.\n")
        
        total_score = 0
        total_weight = 0
        responses = {}
        
        for i, question in enumerate(self.questions, 1):
            print(f"\nQuestion {i}/{len(self.questions)}:")
            print(f"{question.question}\n")
            
            for j, option in enumerate(question.options, 1):
                print(f"{j}. {option}")
            
            while True:
                try:
                    choice = int(input(f"\nYour choice (1-{len(question.options)}): ")) - 1
                    if 0 <= choice < len(question.options):
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
            
            score = question.scores[choice]
            weighted_score = score * question.weight
            total_score += weighted_score
            total_weight += question.weight
            
            responses[f"question_{i}"] = {
                "question": question.question,
                "answer": question.options[choice],
                "score": score
            }
        
        # Calculate final risk score
        final_risk_score = round(total_score / total_weight)
        
        # Additional behavioral analysis
        behavioral_traits = self._analyze_behavioral_traits(responses)
        
        # Determine risk category
        risk_category = self._determine_risk_category(final_risk_score, behavioral_traits)
        
        # Get time horizon from responses
        time_horizon = self._extract_time_horizon(responses)
        
        # Assess financial capacity
        financial_capacity = self._assess_financial_capacity(responses)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(final_risk_score, risk_category, behavioral_traits)
        
        return RiskProfile(
            risk_score=final_risk_score,
            risk_category=risk_category,
            time_horizon=time_horizon,
            financial_capacity=financial_capacity,
            behavioral_traits=behavioral_traits,
            recommendations=recommendations
        )
    
    def _analyze_behavioral_traits(self, responses: Dict) -> Dict[str, str]:
        """Analyze behavioral traits from responses"""
        
        traits = {}
        
        # Loss aversion analysis
        loss_reaction = responses.get("question_2", {}).get("score", 5)
        if loss_reaction <= 3:
            traits["loss_tolerance"] = "Low - May panic during market downturns"
        elif loss_reaction <= 6:
            traits["loss_tolerance"] = "Moderate - Can handle some volatility"
        else:
            traits["loss_tolerance"] = "High - Comfortable with market fluctuations"
        
        # Monitoring behavior
        monitoring = responses.get("question_9", {}).get("score", 5)
        if monitoring <= 4:
            traits["monitoring_style"] = "Active - Frequent monitoring may lead to emotional decisions"
        else:
            traits["monitoring_style"] = "Passive - Long-term focused approach"
        
        # Experience level
        experience = responses.get("question_4", {}).get("score", 5)
        if experience <= 4:
            traits["experience_level"] = "Beginner - Needs education and guidance"
        elif experience <= 6:
            traits["experience_level"] = "Intermediate - Has basic knowledge"
        else:
            traits["experience_level"] = "Advanced - Experienced investor"
        
        return traits
    
    def _determine_risk_category(self, risk_score: int, behavioral_traits: Dict) -> RiskCategory:
        """Determine risk category based on score and behavioral analysis"""
        
        # Adjust score based on behavioral traits
        adjusted_score = risk_score
        
        if "Low" in behavioral_traits.get("loss_tolerance", ""):
            adjusted_score -= 1
        if "Active" in behavioral_traits.get("monitoring_style", ""):
            adjusted_score -= 0.5
        if "Beginner" in behavioral_traits.get("experience_level", ""):
            adjusted_score -= 1
        
        if adjusted_score <= 2:
            return RiskCategory.CONSERVATIVE
        elif adjusted_score <= 4:
            return RiskCategory.MODERATE_CONSERVATIVE
        elif adjusted_score <= 6:
            return RiskCategory.MODERATE
        elif adjusted_score <= 8:
            return RiskCategory.MODERATE_AGGRESSIVE
        else:
            return RiskCategory.AGGRESSIVE
    
    def _extract_time_horizon(self, responses: Dict) -> int:
        """Extract investment time horizon from responses"""
        
        time_score = responses.get("question_3", {}).get("score", 5)
        
        if time_score <= 1:
            return 1
        elif time_score <= 3:
            return 3
        elif time_score <= 5:
            return 7
        elif time_score <= 8:
            return 15
        else:
            return 25
    
    def _assess_financial_capacity(self, responses: Dict) -> str:
        """Assess financial capacity for risk-taking"""
        
        wealth_percentage = responses.get("question_5", {}).get("score", 5)
        income_stability = responses.get("question_6", {}).get("score", 5)
        emergency_fund = responses.get("question_7", {}).get("score", 5)
        
        capacity_score = (wealth_percentage + income_stability + emergency_fund) / 3
        
        if capacity_score >= 7:
            return "High"
        elif capacity_score >= 5:
            return "Medium"
        else:
            return "Low"
    
    def _generate_recommendations(self, risk_score: int, risk_category: RiskCategory, 
                                behavioral_traits: Dict) -> List[str]:
        """Generate personalized recommendations"""
        
        recommendations = []
        
        # Asset allocation recommendations
        if risk_category == RiskCategory.CONSERVATIVE:
            recommendations.append("Asset Allocation: 20% Stocks, 70% Bonds, 10% Cash")
            recommendations.append("Focus on capital preservation and steady income")
        elif risk_category == RiskCategory.MODERATE_CONSERVATIVE:
            recommendations.append("Asset Allocation: 35% Stocks, 60% Bonds, 5% Cash")
            recommendations.append("Emphasize stability with modest growth potential")
        elif risk_category == RiskCategory.MODERATE:
            recommendations.append("Asset Allocation: 50% Stocks, 45% Bonds, 5% Cash")
            recommendations.append("Balanced approach between growth and stability")
        elif risk_category == RiskCategory.MODERATE_AGGRESSIVE:
            recommendations.append("Asset Allocation: 70% Stocks, 25% Bonds, 5% Cash")
            recommendations.append("Growth-focused with some defensive positions")
        else:  # AGGRESSIVE
            recommendations.append("Asset Allocation: 85% Stocks, 10% Bonds, 5% Cash")
            recommendations.append("Maximum growth potential with higher volatility")
        
        # Behavioral recommendations
        if "Low" in behavioral_traits.get("loss_tolerance", ""):
            recommendations.append("Consider dollar-cost averaging to reduce timing risk")
            recommendations.append("Set up automatic investments to avoid emotional decisions")
        
        if "Active" in behavioral_traits.get("monitoring_style", ""):
            recommendations.append("Limit portfolio checking to monthly or quarterly")
            recommendations.append("Focus on long-term goals rather than daily fluctuations")
        
        if "Beginner" in behavioral_traits.get("experience_level", ""):
            recommendations.append("Start with diversified index funds or ETFs")
            recommendations.append("Consider working with a financial advisor")
            recommendations.append("Invest in financial education and learning")
        
        return recommendations

def demo_risk_assessment():
    """Demonstrate risk assessment system"""
    
    assessment = RiskAssessment()
    
    # For demo purposes, simulate responses
    print("=== RISK ASSESSMENT DEMO ===")
    print("This would normally be an interactive assessment.")
    print("Simulating responses for demonstration...\n")
    
    # Simulate a moderate risk profile
    simulated_responses = {
        "question_1": {"score": 5, "answer": "Balanced growth"},
        "question_2": {"score": 6, "answer": "Worried but hold on"},
        "question_3": {"score": 8, "answer": "10-20 years"},
        "question_4": {"score": 5, "answer": "Some experience"},
        "question_5": {"score": 6, "answer": "25-50%"},
        "question_6": {"score": 8, "answer": "Stable income"},
        "question_7": {"score": 6, "answer": "3-6 months covered"},
        "question_8": {"score": 5, "answer": "Moderate risk"},
        "question_9": {"score": 6, "answer": "Monthly check-ins"},
        "question_10": {"score": 5, "answer": "Balanced mutual fund"}
    }
    
    # Calculate simulated profile
    total_score = sum(resp["score"] * 1.5 for resp in simulated_responses.values())  # Average weight
    final_score = round(total_score / (len(simulated_responses) * 1.5))
    
    behavioral_traits = {
        "loss_tolerance": "Moderate - Can handle some volatility",
        "monitoring_style": "Passive - Long-term focused approach",
        "experience_level": "Intermediate - Has basic knowledge"
    }
    
    profile = RiskProfile(
        risk_score=final_score,
        risk_category=RiskCategory.MODERATE,
        time_horizon=15,
        financial_capacity="Medium",
        behavioral_traits=behavioral_traits,
        recommendations=[
            "Asset Allocation: 50% Stocks, 45% Bonds, 5% Cash",
            "Balanced approach between growth and stability",
            "Consider diversified index funds for core holdings"
        ]
    )
    
    print(f"Risk Score: {profile.risk_score}/10")
    print(f"Risk Category: {profile.risk_category.value}")
    print(f"Time Horizon: {profile.time_horizon} years")
    print(f"Financial Capacity: {profile.financial_capacity}")
    print("\nBehavioral Traits:")
    for trait, description in profile.behavioral_traits.items():
        print(f"  - {trait}: {description}")
    print("\nRecommendations:")
    for rec in profile.recommendations:
        print(f"  - {rec}")

if __name__ == "__main__":
    demo_risk_assessment()
