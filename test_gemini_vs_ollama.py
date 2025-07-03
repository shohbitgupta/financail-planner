#!/usr/bin/env python3
"""
Test script to compare Ollama 3.2 vs Gemini CLI for financial planning responses
This script will test both models with the same input and compare results
"""

import json
import time
import requests
from typing import Dict, Any
import google.generativeai as genai

# Test user data
TEST_USER_DATA = {
    "age": 35,
    "retirement_age": 60,
    "annual_salary": 150000,
    "annual_expenses": 80000,
    "current_savings": 50000,
    "goal": "retirement planning",
    "risk_tolerance": "moderate",
    "market_type": "UAE",
    "sharia_compliant": True
}

# Financial planning prompt template
FINANCIAL_PROMPT = """
You are a professional financial advisor specializing in UAE and US markets. Create a comprehensive financial plan for the following client:

**CLIENT PROFILE:**
- Age: {age}
- Target Retirement Age: {retirement_age}
- Annual Salary: ${annual_salary:,}
- Annual Expenses: ${annual_expenses:,}
- Current Savings: ${current_savings:,}
- Investment Goal: {goal}
- Risk Tolerance: {risk_tolerance}
- Market Focus: {market_type}
- Sharia Compliance Required: {sharia_compliant}

**REQUIRED ANALYSIS SECTIONS:**
Please provide detailed analysis in the following sections:

1. **RISK ASSESSMENT**
   - Evaluate client's risk profile
   - Recommend appropriate risk level (1-10 scale)
   - Explain risk tolerance alignment

2. **TIME HORIZON ANALYSIS**
   - Analyze investment timeline
   - Recommend strategy based on years to retirement
   - Identify key milestones

3. **PORTFOLIO RECOMMENDATIONS**
   - Specific instrument recommendations
   - Asset allocation percentages
   - Expected returns for each category

4. **MONTHLY SAVINGS NEEDED**
   - Calculate required monthly investment
   - Show projected wealth accumulation
   - Provide alternative scenarios

5. **ADDITIONAL ADVICE**
   - Tax optimization strategies
   - Emergency fund recommendations
   - Regular review schedule

6. **COMPLIANCE NOTES**
   - Sharia compliance considerations (if applicable)
   - Regulatory requirements
   - Risk disclosures

Please provide specific, actionable recommendations with numerical targets and realistic projections.
"""

class ModelTester:
    def __init__(self):
        """Initialize both Ollama and Gemini models"""
        # Initialize Gemini
        self.gemini_api_key = "AIzaSyBAK741U0ImBRfHgsuPhKFIQrehP1j1_yU"
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Ollama endpoint
        self.ollama_url = "http://localhost:11434/api/generate"
        
        print("Model Tester initialized")
        print("✅ Gemini 2.0 Flash configured")
        print("🔄 Ollama endpoint: localhost:11434")

    def test_ollama_response(self, prompt: str) -> Dict[str, Any]:
        """Test Ollama 3.2 response"""
        print("\n🦙 Testing Ollama 3.2...")
        start_time = time.time()
        
        try:
            payload = {
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            response_time = time.time() - start_time
            
            return {
                "success": True,
                "response": result.get("response", ""),
                "response_time": response_time,
                "model": "Ollama 3.2",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": "",
                "response_time": time.time() - start_time,
                "model": "Ollama 3.2",
                "error": str(e)
            }

    def test_gemini_response(self, prompt: str) -> Dict[str, Any]:
        """Test Gemini response"""
        print("\n💎 Testing Gemini 2.0 Flash...")
        start_time = time.time()
        
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    max_output_tokens=2000,
                )
            )
            
            response_time = time.time() - start_time
            
            return {
                "success": True,
                "response": response.text,
                "response_time": response_time,
                "model": "Gemini 2.0 Flash",
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": "",
                "response_time": time.time() - start_time,
                "model": "Gemini 2.0 Flash",
                "error": str(e)
            }

    def analyze_response_quality(self, response: str) -> Dict[str, Any]:
        """Analyze response quality metrics"""
        if not response:
            return {"score": 0, "details": "Empty response"}
        
        # Check for required sections
        required_sections = [
            "RISK ASSESSMENT",
            "TIME HORIZON",
            "PORTFOLIO",
            "MONTHLY SAVINGS",
            "ADDITIONAL ADVICE",
            "COMPLIANCE"
        ]
        
        sections_found = sum(1 for section in required_sections if section.lower() in response.lower())
        section_score = (sections_found / len(required_sections)) * 100
        
        # Check for specific details
        has_numbers = bool(any(char.isdigit() for char in response))
        has_percentages = "%" in response
        has_currency = "$" in response or "AED" in response
        has_specific_instruments = any(term in response.lower() for term in ["stock", "bond", "etf", "reit", "fund"])
        
        detail_score = sum([has_numbers, has_percentages, has_currency, has_specific_instruments]) * 25
        
        # Overall quality score
        length_score = min(len(response) / 1000 * 100, 100)  # Prefer longer, detailed responses
        
        overall_score = (section_score * 0.4 + detail_score * 0.4 + length_score * 0.2)
        
        return {
            "overall_score": round(overall_score, 2),
            "section_coverage": f"{sections_found}/{len(required_sections)} sections",
            "has_numbers": has_numbers,
            "has_percentages": has_percentages,
            "has_currency": has_currency,
            "has_instruments": has_specific_instruments,
            "response_length": len(response),
            "sections_found": sections_found
        }

    def run_comparison_test(self):
        """Run comparison test between both models"""
        print("🚀 Starting Model Comparison Test")
        print("=" * 60)
        
        # Format prompt with test data
        formatted_prompt = FINANCIAL_PROMPT.format(**TEST_USER_DATA)
        
        # Test both models
        ollama_result = self.test_ollama_response(formatted_prompt)
        gemini_result = self.test_gemini_response(formatted_prompt)
        
        # Analyze responses
        print("\n📊 ANALYSIS RESULTS")
        print("=" * 60)
        
        if ollama_result["success"]:
            ollama_analysis = self.analyze_response_quality(ollama_result["response"])
            print(f"\n🦙 OLLAMA 3.2 RESULTS:")
            print(f"   ✅ Success: {ollama_result['success']}")
            print(f"   ⏱️  Response Time: {ollama_result['response_time']:.2f}s")
            print(f"   📈 Quality Score: {ollama_analysis['overall_score']}/100")
            print(f"   📋 Section Coverage: {ollama_analysis['section_coverage']}")
            print(f"   📏 Response Length: {ollama_analysis['response_length']} chars")
        else:
            print(f"\n🦙 OLLAMA 3.2 RESULTS:")
            print(f"   ❌ Failed: {ollama_result['error']}")
        
        if gemini_result["success"]:
            gemini_analysis = self.analyze_response_quality(gemini_result["response"])
            print(f"\n💎 GEMINI 2.0 FLASH RESULTS:")
            print(f"   ✅ Success: {gemini_result['success']}")
            print(f"   ⏱️  Response Time: {gemini_result['response_time']:.2f}s")
            print(f"   📈 Quality Score: {gemini_analysis['overall_score']}/100")
            print(f"   📋 Section Coverage: {gemini_analysis['section_coverage']}")
            print(f"   📏 Response Length: {gemini_analysis['response_length']} chars")
        else:
            print(f"\n💎 GEMINI 2.0 FLASH RESULTS:")
            print(f"   ❌ Failed: {gemini_result['error']}")
        
        # Recommendation
        print(f"\n🎯 RECOMMENDATION")
        print("=" * 60)
        
        if ollama_result["success"] and gemini_result["success"]:
            ollama_score = self.analyze_response_quality(ollama_result["response"])["overall_score"]
            gemini_score = self.analyze_response_quality(gemini_result["response"])["overall_score"]
            
            if gemini_score > ollama_score:
                print(f"💎 GEMINI 2.0 FLASH is recommended")
                print(f"   • Higher quality score: {gemini_score} vs {ollama_score}")
                print(f"   • Better response time: {gemini_result['response_time']:.2f}s vs {ollama_result['response_time']:.2f}s")
                print(f"   • More reliable cloud-based service")
            else:
                print(f"🦙 OLLAMA 3.2 is recommended")
                print(f"   • Higher quality score: {ollama_score} vs {gemini_score}")
                print(f"   • Local processing (privacy)")
        elif gemini_result["success"]:
            print(f"💎 GEMINI 2.0 FLASH is recommended (Ollama failed)")
        elif ollama_result["success"]:
            print(f"🦙 OLLAMA 3.2 is recommended (Gemini failed)")
        else:
            print(f"❌ Both models failed - check configurations")
        
        # Save detailed results
        results = {
            "test_timestamp": time.time(),
            "test_user_data": TEST_USER_DATA,
            "ollama_result": ollama_result,
            "gemini_result": gemini_result
        }
        
        if ollama_result["success"]:
            results["ollama_analysis"] = self.analyze_response_quality(ollama_result["response"])
        if gemini_result["success"]:
            results["gemini_analysis"] = self.analyze_response_quality(gemini_result["response"])
        
        with open("model_comparison_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: model_comparison_results.json")
        
        return results

if __name__ == "__main__":
    tester = ModelTester()
    results = tester.run_comparison_test()
