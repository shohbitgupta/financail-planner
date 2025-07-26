import React, { useState } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { DollarSign, Target, Shield, Clock, AlertCircle, CheckCircle, User, Send, Calculator, ChevronDown, ChevronUp, Info, TrendingUp, TrendingDown, MessageCircle } from 'lucide-react';
import ChatBasedInput from './ChatBasedInput';
import FeedbackSystem from './FeedbackSystem';
import { getApiUrl, API_CONFIG } from '../config';

// Type definitions
interface UserProfile {
  age: number;
  retirement_age: number;
  annual_salary: number;
  annual_expenses: number;
  current_savings: number;
  monthly_investment: number;
  risk_tolerance: string;
  investment_horizon: number;
  goals: string[];
  is_sharia_compliant: boolean;
  preferred_market: string;
  currency: string;
}

interface UserInputForm {
  age: string;
  retirement_age: string;
  annual_salary: string;
  annual_expenses: string;
  current_savings: string;
  monthly_investment: string;
  risk_tolerance: string;
  goals: string[];
  is_sharia_compliant: boolean;
  preferred_market: string;
  currency: string;
}

interface Recommendation {
  symbol: string;
  name: string;
  category: string;
  allocation_percentage: number;
  investment_amount: number;
  rationale: string;
  risk_level: number;
  expected_return: number;
  market: string;
  currency?: string;
  min_investment?: number;
  expense_ratio?: number;
  dividend_yield?: number;
  volatility?: number;
  sharpe_ratio?: number;
  ytd_return?: number;
  three_year_return?: number;
  five_year_return?: number;
  max_drawdown?: number;
  platform_recommendation?: {
    platform_name: string;
    platform_type: string;
    app_name?: string;
    features: string[];
    setup_steps: string[];
    benefits: string[];
  };
}

interface EvaluationMetadata {
  evaluator_used: boolean;
  original_score: number;
  improvement_applied: boolean;
  evaluation_timestamp: string;
  improvement_details?: {
    original_score: number;
    improved_score: number;
    score_improvement: number;
    threshold: number;
    improvement_reason: string;
  };
  detailed_comparison?: {
    score_changes: { [key: string]: any };
    feedback_comparison: { [key: string]: any };
    key_improvements: string[];
    areas_enhanced: any[];
  };
  evaluation_criteria?: { [key: string]: any };
  original_evaluation?: { [key: string]: any };
  gemini_responses?: {
    original_response: string;
    final_response: string;
  };
}

interface ResponseMetadata {
  llm_source: string;
  session_id: string;
  user_id: string;
  response_strategy: any;
  llamacloud_used: boolean;
  vector_context_available: boolean;
  timestamp: string;
}

interface RiskAssessment {
  risk_level?: string;
  description: string;
  suitability?: string;
  recommended_allocation?: string;
  time_factor?: string;
  age_factor?: string;
}

interface TimeHorizonAnalysis {
  horizon_category?: string;
  strategy?: string;
  flexibility?: string;
  milestones?: {
    short_term?: string;
    medium_term?: string;
    long_term?: string;
  };
  retirement_readiness?: string;
  description?: string;
}

interface GoalRiskMitigation {
  [goalName: string]: {
    risks: string[];
    mitigation: string[];
  };
}

interface FinancialPlan {
  user_profile: UserProfile;
  recommendations: Recommendation[];
  total_allocation: Record<string, number>;
  risk_assessment: RiskAssessment | string;
  time_horizon_analysis: TimeHorizonAnalysis | string;
  expected_portfolio_return: number;
  monthly_savings_needed: number;
  goal_achievement_timeline: Record<string, number>;
  additional_advice: string[];
  goal_risks_mitigation?: GoalRiskMitigation;
  compliance_notes: string;
  evaluation_metadata?: EvaluationMetadata;
  response_metadata?: ResponseMetadata;
  raw_llm_response?: string;
}

interface MarketData {
  market: string;
  allocation: number;
  amount: number;
}

interface PieData {
  name: string;
  value: number;
}

interface BarData {
  name: string;
  allocation: number;
  amount: number;
  risk: number;
  return: number;
}

// Sample financial plan data (in real app, this would come from your API)
const sampleFinancialPlan: FinancialPlan = {
  user_profile: {
    age: 35,
    retirement_age: 60,
    annual_salary: 200000,
    annual_expenses: 120000,
    current_savings: 50000,
    monthly_investment: 5000,
    risk_tolerance: "moderate",
    investment_horizon: 25,
    goals: ["retirement", "wealth_building"],
    is_sharia_compliant: true,
    preferred_market: "BOTH",
    currency: "AED"
  },
  recommendations: [
    {
      symbol: "UAEETF",
      name: "UAE Equity ETF",
      category: "ETF",
      allocation_percentage: 30,
      investment_amount: 1500,
      rationale: "Provides exposure to UAE market with Sharia compliance",
      risk_level: 6,
      expected_return: 0.08,
      market: "UAE"
    },
    {
      symbol: "FAB",
      name: "First Abu Dhabi Bank",
      category: "Banking",
      allocation_percentage: 25,
      investment_amount: 1250,
      rationale: "Strong banking sector exposure in UAE market",
      risk_level: 6,
      expected_return: 0.08,
      market: "UAE"
    },
    {
      symbol: "SUKUK5Y",
      name: "UAE Sukuk 5Y",
      category: "Islamic Bond",
      allocation_percentage: 25,
      investment_amount: 1250,
      rationale: "Conservative Sharia-compliant fixed income",
      risk_level: 3,
      expected_return: 0.04,
      market: "UAE"
    },
    {
      symbol: "GLD",
      name: "SPDR Gold Shares",
      category: "Commodity ETF",
      allocation_percentage: 20,
      investment_amount: 1000,
      rationale: "Portfolio diversification and inflation hedge",
      risk_level: 4,
      expected_return: 0.06,
      market: "US"
    }
  ],
  total_allocation: {
    "ETF": 30,
    "Banking": 25,
    "Islamic Bond": 25,
    "Commodity ETF": 20
  },
  risk_assessment: {
    risk_level: "Moderate Risk (5/10)",
    description: "Balanced approach between growth and stability with Islamic compliance",
    suitability: "Long-term investors comfortable with market fluctuations",
    recommended_allocation: "Mix of Sharia-compliant stocks, Islamic bonds, and alternative investments",
    time_factor: "With 20 years to invest, moderate risk tolerance is appropriate",
    age_factor: "At age 35, you have ample time to recover from market downturns"
  },
  time_horizon_analysis: {
    horizon_category: "Long-term (20 years)",
    strategy: "Growth-focused strategy with Islamic compliance emphasis",
    flexibility: "High flexibility to weather market cycles",
    milestones: {
      short_term: "Years 1-5: Build emergency fund and establish halal investment routine",
      medium_term: "Years 6-15: Accumulate wealth through Sharia-compliant instruments",
      long_term: "Years 16-20: Maximize growth while preparing for retirement"
    },
    retirement_readiness: "Target retirement at age 55 with 20 years of Islamic wealth accumulation"
  },
  expected_portfolio_return: 0.068,
  monthly_savings_needed: 5000,
  goal_achievement_timeline: {
    "retirement": 20,
    "wealth_building": 15
  },
  additional_advice: [
    "Review and rebalance your portfolio quarterly to maintain target allocation",
    "Increase monthly investments by 5-10% annually as income grows",
    "Maintain an emergency fund covering 3-6 months of expenses",
    "Ensure all investments maintain Sharia compliance through regular screening",
    "Take advantage of long investment horizon with growth-focused allocations"
  ],
  goal_risks_mitigation: {
    "retirement": {
      "risks": [
        "Market volatility affecting long-term returns",
        "Inflation eroding purchasing power over time",
        "Sequence of returns risk near retirement",
        "Healthcare cost increases in retirement"
      ],
      "mitigation": [
        "Diversified portfolio across asset classes",
        "Inflation-protected securities allocation",
        "Gradual shift to conservative investments near retirement",
        "Health savings account and insurance planning"
      ]
    },
    "wealth_building": {
      "risks": [
        "Market cycles affecting growth trajectory",
        "Lifestyle inflation reducing savings rate",
        "Economic downturns impacting income",
        "Lack of investment discipline"
      ],
      "mitigation": [
        "Dollar-cost averaging strategy",
        "Automatic savings and investment plans",
        "Emergency fund maintenance",
        "Regular portfolio reviews and rebalancing"
      ]
    }
  },
  compliance_notes: "All recommendations meet Sharia compliance requirements"
};

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

// Helper function to parse LLM response into sections
const parseLLMResponseSections = (response: string): Record<string, string> => {
  const sections: Record<string, string> = {};

  // Define section patterns
  const sectionPatterns = [
    'EXECUTIVE SUMMARY',
    'PORTFOLIO RECOMMENDATIONS',
    'RISK ASSESSMENT',
    'TIME HORIZON ANALYSIS',
    'MONTHLY SAVINGS NEEDED',
    'GOAL ACHIEVEMENT TIMELINE',
    'ADDITIONAL ADVICE',
    'COMPLIANCE NOTES',
    'INVESTMENT STRATEGY',
    'MARKET ANALYSIS',
    'DIVERSIFICATION STRATEGY'
  ];

  sectionPatterns.forEach(sectionName => {
    const pattern = new RegExp(`${sectionName}[:\\s]*\\n(.*?)(?=\\n(?:${sectionPatterns.join('|')})|\\Z)`, 'is');
    const match = response.match(pattern);
    if (match && match[1]) {
      sections[sectionName] = match[1].trim();
    }
  });

  // If no sections found, return the entire response as "FULL RESPONSE"
  if (Object.keys(sections).length === 0) {
    sections['FULL RESPONSE'] = response;
  }

  return sections;
};

const FinancialPlannerDashboard: React.FC = () => {
  const [plan, setPlan] = useState<FinancialPlan | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [showInputForm, setShowInputForm] = useState<boolean>(true);
  const [useChatInput, setUseChatInput] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [expandedRecommendations, setExpandedRecommendations] = useState<Set<string>>(new Set());
  const [userInput, setUserInput] = useState<UserInputForm>({
    age: '',
    retirement_age: '',
    annual_salary: '',
    annual_expenses: '',
    current_savings: '',
    monthly_investment: '',
    risk_tolerance: 'moderate',
    goals: [],
    is_sharia_compliant: false,
    preferred_market: 'BOTH',
    currency: 'AED'
  });

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-AE', {
      style: 'currency',
      currency: plan?.user_profile.currency || 'AED',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercentage = (value: number): string => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // Function to generate platform recommendation based on category
  const generatePlatformRecommendation = (category: string) => {
    const categoryLower = category.toLowerCase();

    if (categoryLower.includes('equity') || categoryLower.includes('stock') || categoryLower.includes('etf')) {
      return {
        platform_name: "WIO Bank",
        app_name: "WIO Invest App",
        platform_type: "Digital Investment Platform",
        features: ["Stock Trading", "ETF Investments", "Portfolio Management"],
        setup_steps: ["Download WIO Invest App", "Complete KYC", "Fund Account", "Start Investing"],
        benefits: ["Commission-free trading", "Real-time market data", "Professional research"]
      };
    } else if (categoryLower.includes('bond') || categoryLower.includes('fixed income') || categoryLower.includes('sukuk')) {
      return {
        platform_name: "WIO Bank",
        app_name: "WIO Personal - Saving Spaces",
        platform_type: "Digital Savings Platform",
        features: ["Fixed Income Products", "Saving Goals", "Automated Savings"],
        setup_steps: ["Open WIO Personal Account", "Set Saving Goals", "Configure Auto-transfers"],
        benefits: ["Competitive returns", "Goal-based saving", "Flexible terms"]
      };
    } else if (categoryLower.includes('real estate') || categoryLower.includes('reit') || categoryLower.includes('property')) {
      return {
        platform_name: "WIO Bank",
        app_name: "WIO Banking App",
        platform_type: "Comprehensive Digital Banking",
        features: ["Real Estate Financing", "Investment Banking", "Wealth Management"],
        setup_steps: ["Open WIO Banking Account", "Complete Investment Profile", "Access Real Estate Products"],
        benefits: ["Competitive financing rates", "Expert advisory", "Integrated banking services"]
      };
    } else {
      // Default to WIO Invest for other investment types
      return {
        platform_name: "WIO Bank",
        app_name: "WIO Invest App",
        platform_type: "Digital Investment Platform",
        features: ["Investment Products", "Portfolio Management", "Market Research"],
        setup_steps: ["Download WIO Invest App", "Complete Registration", "Start Investing"],
        benefits: ["Professional platform", "Research tools", "Competitive pricing"]
      };
    }
  };

  const toggleRecommendationExpansion = (symbol: string) => {
    setExpandedRecommendations(prev => {
      const newSet = new Set(prev);
      if (newSet.has(symbol)) {
        newSet.delete(symbol);
      } else {
        newSet.add(symbol);
      }
      return newSet;
    });
  };

  const handleInputChange = (field: keyof UserInputForm, value: string | boolean | string[]) => {
    setUserInput(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleGoalToggle = (goal: string) => {
    setUserInput(prev => ({
      ...prev,
      goals: prev.goals.includes(goal)
        ? prev.goals.filter(g => g !== goal)
        : [...prev.goals, goal]
    }));
  };

  const handleChatComplete = async (chatUserData: any) => {
    setIsLoading(true);

    try {
      console.log('Received data from chat:', chatUserData);

      const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.GENERATE_PLAN), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(chatUserData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Received data from API:', data);
      console.log('Recommendations with platform data:', data.recommendations?.map((rec: any) => ({
        name: rec.name,
        category: rec.category,
        has_platform_recommendation: !!rec.platform_recommendation,
        platform_name: rec.platform_recommendation?.platform_name
      })));

      setPlan(data);
      setShowInputForm(false);
    } catch (error) {
      console.error('Error generating financial plan:', error);
      alert('Failed to generate financial plan. Please check if the Flask API is running on port 5001.');
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = (): boolean => {
    const requiredFields = ['age', 'retirement_age', 'annual_salary', 'annual_expenses', 'current_savings'];
    return requiredFields.every(field => userInput[field as keyof UserInputForm] !== '');
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }

    if (!validateForm()) {
      alert('Please fill in all required fields');
      return;
    }

    setIsLoading(true);

    try {
      // Call Flask API with Ollama integration
      const response = await fetch(getApiUrl(API_CONFIG.ENDPOINTS.GENERATE_PLAN), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          age: parseInt(userInput.age),
          retirement_age: parseInt(userInput.retirement_age),
          annual_salary: parseFloat(userInput.annual_salary),
          annual_expenses: parseFloat(userInput.annual_expenses),
          current_savings: parseFloat(userInput.current_savings),
          monthly_investment: parseFloat(userInput.monthly_investment) || 0,
          risk_tolerance: userInput.risk_tolerance,
          goals: userInput.goals,
          is_sharia_compliant: userInput.is_sharia_compliant,
          preferred_market: userInput.preferred_market,
          currency: userInput.currency
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const financialPlan = await response.json();

      if (financialPlan.error) {
        throw new Error(financialPlan.error);
      }

      console.log('Received financial plan:', financialPlan);
      console.log('Form Recommendations with platform data:', financialPlan.recommendations?.map((rec: any) => ({
        name: rec.name,
        category: rec.category,
        has_platform_recommendation: !!rec.platform_recommendation,
        platform_name: rec.platform_recommendation?.platform_name
      })));
      setPlan(financialPlan);
      setShowInputForm(false);
      setIsLoading(false);

    } catch (error) {
      console.error('Error generating financial plan:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      alert(`Failed to generate financial plan: ${errorMessage}. Please make sure the Flask API is running on port 5001.`);
      setIsLoading(false);
    }
  };

  const handleNewPlan = () => {
    setPlan(null);
    setShowInputForm(true);
    setUserInput({
      age: '',
      retirement_age: '',
      annual_salary: '',
      annual_expenses: '',
      current_savings: '',
      monthly_investment: '',
      risk_tolerance: 'moderate',
      goals: [],
      is_sharia_compliant: false,
      preferred_market: 'BOTH',
      currency: 'AED'
    });
  };

  // Show input form if no plan exists or if showInputForm is true
  if (!plan || showInputForm) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Financial Planner AI</h1>
              <p className="text-gray-600">Chat with our AI to get personalized investment recommendations</p>

              {/* Input Method Toggle */}
              <div className="flex justify-center mt-4 space-x-4">
                <button
                  onClick={() => setUseChatInput(true)}
                  className={`px-4 py-2 rounded-md flex items-center ${
                    useChatInput
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  <MessageCircle className="h-4 w-4 mr-2" />
                  Chat Input
                </button>
                <button
                  onClick={() => setUseChatInput(false)}
                  className={`px-4 py-2 rounded-md flex items-center ${
                    !useChatInput
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  <User className="h-4 w-4 mr-2" />
                  Form Input
                </button>
              </div>
            </div>

            {/* Chat-based Input */}
            {useChatInput ? (
              <div className="max-w-2xl mx-auto">
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Generating your personalized financial plan...</p>
                  </div>
                ) : (
                  <ChatBasedInput
                    onComplete={handleChatComplete}
                    onCancel={() => setShowInputForm(false)}
                  />
                )}
              </div>
            ) : (
              // Original Form Input
              <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Current Age</label>
                  <input
                    type="number"
                    value={userInput.age}
                    onChange={(e) => handleInputChange('age', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 35"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Target Retirement Age</label>
                  <input
                    type="number"
                    value={userInput.retirement_age}
                    onChange={(e) => handleInputChange('retirement_age', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 60"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Annual Salary (AED)</label>
                  <input
                    type="number"
                    value={userInput.annual_salary}
                    onChange={(e) => handleInputChange('annual_salary', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 200000"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Annual Expenses (AED)</label>
                  <input
                    type="number"
                    value={userInput.annual_expenses}
                    onChange={(e) => handleInputChange('annual_expenses', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 120000"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Current Savings (AED)</label>
                  <input
                    type="number"
                    value={userInput.current_savings}
                    onChange={(e) => handleInputChange('current_savings', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 50000"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Monthly Investment Capacity (AED)</label>
                  <input
                    type="number"
                    value={userInput.monthly_investment}
                    onChange={(e) => handleInputChange('monthly_investment', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., 5000"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Risk Appetite</label>
                  <select
                    value={userInput.risk_tolerance}
                    onChange={(e) => handleInputChange('risk_tolerance', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="conservative">Conservative</option>
                    <option value="moderate">Moderate</option>
                    <option value="aggressive">Aggressive</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Market Preference</label>
                  <select
                    value={userInput.preferred_market}
                    onChange={(e) => handleInputChange('preferred_market', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="UAE">UAE Market</option>
                    <option value="US">US Market</option>
                    <option value="BOTH">Both Markets</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
                  <select
                    value={userInput.currency}
                    onChange={(e) => handleInputChange('currency', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="AED">AED</option>
                    <option value="USD">USD</option>
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={userInput.is_sharia_compliant}
                      onChange={(e) => handleInputChange('is_sharia_compliant', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm font-medium text-gray-700">Sharia Compliant Investments</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Investment Goals (Select all that apply)</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {['retirement', 'wealth_building', 'education', 'house_purchase', 'emergency_fund', 'travel'].map((goal) => (
                    <label key={goal} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={userInput.goals.includes(goal)}
                        onChange={() => handleGoalToggle(goal)}
                        className="mr-2"
                      />
                      <span className="text-sm text-gray-700 capitalize">{goal.replace('_', ' ')}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex justify-center">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {isLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      Generating AI Plan...
                    </>
                  ) : (
                    'Generate AI Financial Plan'
                  )}
                </button>
              </div>
            </form>
            )}
          </div>
        </div>
      </div>
    );
  }

  const pieData: PieData[] = Object.entries(plan.total_allocation).map(([category, percentage]) => ({
    name: category,
    value: percentage
  }));

  const barData: BarData[] = plan.recommendations.map(rec => ({
    name: rec.symbol,
    allocation: rec.allocation_percentage,
    amount: rec.investment_amount,
    risk: rec.risk_level,
    return: rec.expected_return * 100
  }));

  const marketData: MarketData[] = plan.recommendations.reduce((acc: MarketData[], rec) => {
    const existing = acc.find(item => item.market === rec.market);
    if (existing) {
      existing.allocation += rec.allocation_percentage;
      existing.amount += rec.investment_amount;
    } else {
      acc.push({
        market: rec.market,
        allocation: rec.allocation_percentage,
        amount: rec.investment_amount
      });
    }
    return acc;
  }, []);



  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Financial Planning Dashboard</h1>
              <p className="text-gray-600">Personalized investment recommendations and portfolio analysis</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-sm text-gray-500">Expected Return</div>
                <div className="text-2xl font-bold text-green-600">{formatPercentage(plan.expected_portfolio_return)}</div>
              </div>
              <button
                onClick={handleNewPlan}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center"
              >
                <User className="h-4 w-4 mr-2" />
                New Plan
              </button>
            </div>
          </div>
        </div>

        {/* User Profile Summary */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm text-gray-500">Current Savings</p>
                <p className="text-lg font-semibold">{formatCurrency(plan.user_profile.current_savings)}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-4">
            <div className="flex items-center">
              <Target className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm text-gray-500">Retirement Age</p>
                <p className="text-lg font-semibold">{plan.user_profile.retirement_age} years</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-4">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-yellow-600" />
              <div className="ml-3">
                <p className="text-sm text-gray-500">Risk Tolerance</p>
                <p className="text-lg font-semibold capitalize">{plan.user_profile.risk_tolerance}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-4">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm text-gray-500">Sharia Compliant</p>
                <p className="text-lg font-semibold">{plan.user_profile.is_sharia_compliant ? 'Yes' : 'No'}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-lg mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {['overview', 'recommendations', 'analysis', 'goals', 'details'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm capitalize ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Asset Allocation</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, value }) => `${name}: ${value}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {pieData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Market Distribution</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={marketData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="market" />
                      <YAxis />
                      <Tooltip formatter={(value, name) => [
                        name === 'allocation' ? `${value}%` : formatCurrency(Number(value)),
                        name === 'allocation' ? 'Allocation' : 'Amount'
                      ]} />
                      <Bar dataKey="allocation" fill="#8884d8" name="allocation" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Recommendations Tab */}
            {activeTab === 'recommendations' && (
              <div>
                <h3 className="text-lg font-semibold mb-6">Investment Recommendations by Segment</h3>

                {/* Group recommendations by category */}
                {(() => {
                  const groupedRecommendations = plan.recommendations.reduce((groups: Record<string, Recommendation[]>, rec) => {
                    const category = rec.category || 'Other';
                    if (!groups[category]) {
                      groups[category] = [];
                    }
                    groups[category].push(rec);
                    return groups;
                  }, {});

                  return Object.entries(groupedRecommendations).map(([category, recommendations]) => (
                    <div key={category} className="mb-8">
                      {/* Category Header */}
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="text-xl font-semibold text-blue-900">{category}</h4>
                            <p className="text-blue-700 text-sm mt-1">
                              {recommendations.length} instrument{recommendations.length > 1 ? 's' : ''} •
                              {recommendations.reduce((sum, rec) => sum + rec.allocation_percentage, 0).toFixed(1)}% total allocation
                            </p>
                          </div>
                          <div className="text-right">
                            <div className="text-2xl font-bold text-blue-600">
                              {formatCurrency(recommendations.reduce((sum, rec) => sum + rec.investment_amount, 0))}
                            </div>
                            <div className="text-sm text-blue-700">Monthly Investment</div>
                          </div>
                        </div>

                        {/* Category Analysis */}
                        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="bg-white rounded-lg p-3">
                            <div className="text-sm text-gray-600">Avg Expected Return</div>
                            <div className="text-lg font-semibold text-green-600">
                              {formatPercentage(recommendations.reduce((sum, rec) => sum + rec.expected_return, 0) / recommendations.length)}
                            </div>
                          </div>
                          <div className="bg-white rounded-lg p-3">
                            <div className="text-sm text-gray-600">Avg Risk Level</div>
                            <div className="text-lg font-semibold text-orange-600">
                              {(recommendations.reduce((sum, rec) => sum + rec.risk_level, 0) / recommendations.length).toFixed(1)}/10
                            </div>
                          </div>
                          <div className="bg-white rounded-lg p-3">
                            <div className="text-sm text-gray-600">Market Exposure</div>
                            <div className="text-lg font-semibold text-blue-600">
                              {Array.from(new Set(recommendations.map(rec => rec.market))).join(', ')}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Individual Recommendations in this Category */}
                      <div className="space-y-4">
                        {recommendations.map((rec, index) => {
                    const isExpanded = expandedRecommendations.has(rec.symbol);
                    // Ensure platform recommendation exists, generate if missing
                    const platformRecommendation = rec.platform_recommendation || generatePlatformRecommendation(rec.category);
                    const recWithPlatform = { ...rec, platform_recommendation: platformRecommendation };
                    return (
                      <div key={index} className="border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                        {/* Main recommendation card */}
                        <div className="p-4">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3">
                                <h4 className="text-lg font-semibold text-gray-900">{recWithPlatform.symbol}</h4>
                                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">{recWithPlatform.market}</span>
                                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">{recWithPlatform.category}</span>
                                {/* WIO Platform Badge */}
                                {recWithPlatform.platform_recommendation && (
                                  <span className="px-3 py-1 bg-gradient-to-r from-purple-500 to-purple-600 text-white text-xs font-bold rounded-full shadow-md">
                                    🏦 {recWithPlatform.platform_recommendation.app_name || recWithPlatform.platform_recommendation.platform_name}
                                  </span>
                                )}
                              </div>
                              <p className="text-gray-600 font-medium">{recWithPlatform.name}</p>
                              {/* WIO Platform Quick Info */}
                              {recWithPlatform.platform_recommendation && (
                                <div className="mt-2 p-2 bg-purple-50 border border-purple-200 rounded-md">
                                  <p className="text-sm text-purple-800 font-medium">
                                    📱 Available on: <span className="font-bold">{recWithPlatform.platform_recommendation.app_name || recWithPlatform.platform_recommendation.platform_name}</span>
                                  </p>
                                  <p className="text-xs text-purple-600 mt-1">
                                    {recWithPlatform.platform_recommendation.platform_type}
                                  </p>
                                </div>
                              )}
                              <p className="text-sm text-gray-500 mt-2">{recWithPlatform.rationale}</p>
                            </div>
                            <div className="text-right">
                              <div className="text-2xl font-bold text-blue-600">{recWithPlatform.allocation_percentage}%</div>
                              <div className="text-sm text-gray-500">{formatCurrency(recWithPlatform.investment_amount)}/month</div>
                              <div className="text-xs text-gray-400 mt-1">
                                Risk: {recWithPlatform.risk_level}/10 | Return: {formatPercentage(recWithPlatform.expected_return)}
                              </div>
                            </div>
                          </div>

                          {/* Expand/Collapse button */}
                          <div className="mt-4 pt-3 border-t border-gray-100">
                            <button
                              onClick={() => toggleRecommendationExpansion(recWithPlatform.symbol)}
                              className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 transition-colors"
                            >
                              <Info className="h-4 w-4" />
                              <span className="text-sm font-medium">
                                {isExpanded ? 'Hide Details' : 'View Details'}
                              </span>
                              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                            </button>
                          </div>
                        </div>

                        {/* Expanded details */}
                        {isExpanded && (
                          <div className="border-t border-gray-200 bg-gray-50 p-6">
                            {/* Detailed Analysis Section */}
                            <div className="mb-6">
                              <h5 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                                <TrendingUp className="h-5 w-5 mr-2 text-blue-600" />
                                Investment Analysis & Rationale
                              </h5>
                              <div className="bg-white rounded-lg p-4 border border-gray-200">
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                  <div>
                                    <h6 className="font-medium text-gray-900 mb-2">Why This Investment?</h6>
                                    <p className="text-gray-700 text-sm leading-relaxed mb-4">{recWithPlatform.rationale}</p>

                                    <h6 className="font-medium text-gray-900 mb-2">Key Strengths</h6>
                                    <ul className="text-sm text-gray-700 space-y-1">
                                      {recWithPlatform.market === 'UAE' && (
                                        <li className="flex items-center">
                                          <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                                          Local market exposure with regulatory familiarity
                                        </li>
                                      )}
                                      {recWithPlatform.market === 'US' && (
                                        <li className="flex items-center">
                                          <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                                          Access to world's largest and most liquid market
                                        </li>
                                      )}
                                      {recWithPlatform.category.includes('ETF') && (
                                        <li className="flex items-center">
                                          <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                                          Instant diversification across multiple holdings
                                        </li>
                                      )}
                                      {recWithPlatform.category.includes('Bond') && (
                                        <li className="flex items-center">
                                          <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                                          Stable income generation with lower volatility
                                        </li>
                                      )}
                                      {recWithPlatform.expected_return > 0.07 && (
                                        <li className="flex items-center">
                                          <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                                          Above-average expected returns
                                        </li>
                                      )}
                                    </ul>
                                  </div>

                                  <div>
                                    <h6 className="font-medium text-gray-900 mb-2">Risk Considerations</h6>
                                    <div className="space-y-2 text-sm">
                                      <div className="flex items-center justify-between p-2 bg-gray-50 rounded">
                                        <span>Risk Level:</span>
                                        <div className="flex items-center">
                                          <div className="flex space-x-1 mr-2">
                                            {[...Array(10)].map((_, i) => (
                                              <div
                                                key={i}
                                                className={`w-2 h-2 rounded-full ${
                                                  i < recWithPlatform.risk_level
                                                    ? recWithPlatform.risk_level <= 3 ? 'bg-green-500'
                                                      : recWithPlatform.risk_level <= 6 ? 'bg-yellow-500'
                                                      : 'bg-red-500'
                                                    : 'bg-gray-300'
                                                }`}
                                              />
                                            ))}
                                          </div>
                                          <span className="font-medium">{recWithPlatform.risk_level}/10</span>
                                        </div>
                                      </div>

                                      <div className="text-gray-600">
                                        {recWithPlatform.risk_level <= 3 && "Conservative investment with low volatility"}
                                        {recWithPlatform.risk_level > 3 && recWithPlatform.risk_level <= 6 && "Moderate risk with balanced growth potential"}
                                        {recWithPlatform.risk_level > 6 && "Higher risk investment with significant growth potential"}
                                      </div>
                                    </div>

                                    <h6 className="font-medium text-gray-900 mb-2 mt-4">Expected Outcomes</h6>
                                    <div className="space-y-2 text-sm">
                                      <div className="flex justify-between p-2 bg-green-50 rounded">
                                        <span>Annual Return Target:</span>
                                        <span className="font-medium text-green-700">{formatPercentage(recWithPlatform.expected_return)}</span>
                                      </div>
                                      <div className="flex justify-between p-2 bg-blue-50 rounded">
                                        <span>Monthly Investment:</span>
                                        <span className="font-medium text-blue-700">{formatCurrency(recWithPlatform.investment_amount)}</span>
                                      </div>
                                      <div className="flex justify-between p-2 bg-purple-50 rounded">
                                        <span>Portfolio Weight:</span>
                                        <span className="font-medium text-purple-700">{recWithPlatform.allocation_percentage}%</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* Performance & Risk Metrics Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                              {/* Performance Metrics */}
                              <div className="bg-white rounded-lg p-3">
                                <h5 className="font-semibold text-gray-900 mb-2 flex items-center">
                                  <TrendingUp className="h-4 w-4 mr-2 text-green-600" />
                                  Performance
                                </h5>
                                <div className="space-y-2 text-sm">
                                  {recWithPlatform.ytd_return !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">YTD Return:</span>
                                      <span className={`font-medium ${recWithPlatform.ytd_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatPercentage(recWithPlatform.ytd_return)}
                                      </span>
                                    </div>
                                  )}
                                  {recWithPlatform.three_year_return !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">3-Year Return:</span>
                                      <span className={`font-medium ${recWithPlatform.three_year_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatPercentage(recWithPlatform.three_year_return)}
                                      </span>
                                    </div>
                                  )}
                                  {recWithPlatform.five_year_return !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">5-Year Return:</span>
                                      <span className={`font-medium ${recWithPlatform.five_year_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                        {formatPercentage(recWithPlatform.five_year_return)}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              </div>

                              {/* Risk Metrics */}
                              <div className="bg-white rounded-lg p-3">
                                <h5 className="font-semibold text-gray-900 mb-2 flex items-center">
                                  <Shield className="h-4 w-4 mr-2 text-orange-600" />
                                  Risk Analysis
                                </h5>
                                <div className="space-y-2 text-sm">
                                  {recWithPlatform.volatility !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Volatility:</span>
                                      <span className="font-medium text-orange-600">
                                        {formatPercentage(recWithPlatform.volatility)}
                                      </span>
                                    </div>
                                  )}
                                  {recWithPlatform.sharpe_ratio !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Sharpe Ratio:</span>
                                      <span className="font-medium text-blue-600">
                                        {recWithPlatform.sharpe_ratio.toFixed(2)}
                                      </span>
                                    </div>
                                  )}
                                  {recWithPlatform.max_drawdown !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Max Drawdown:</span>
                                      <span className="font-medium text-red-600">
                                        {formatPercentage(Math.abs(recWithPlatform.max_drawdown))}
                                      </span>
                                    </div>
                                  )}
                                </div>
                              </div>

                              {/* Investment Details */}
                              <div className="bg-white rounded-lg p-3">
                                <h5 className="font-semibold text-gray-900 mb-2 flex items-center">
                                  <DollarSign className="h-4 w-4 mr-2 text-blue-600" />
                                  Investment Info
                                </h5>
                                <div className="space-y-2 text-sm">
                                  {recWithPlatform.min_investment !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Min Investment:</span>
                                      <span className="font-medium text-gray-900">
                                        {formatCurrency(recWithPlatform.min_investment)}
                                      </span>
                                    </div>
                                  )}
                                  {recWithPlatform.expense_ratio !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Expense Ratio:</span>
                                      <span className="font-medium text-gray-900">
                                        {formatPercentage(recWithPlatform.expense_ratio / 100)}
                                      </span>
                                    </div>
                                  )}
                                  {recWithPlatform.dividend_yield !== undefined && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Dividend Yield:</span>
                                      <span className="font-medium text-green-600">
                                        {formatPercentage(recWithPlatform.dividend_yield / 100)}
                                      </span>
                                    </div>
                                  )}
                                  {recWithPlatform.currency && (
                                    <div className="flex justify-between">
                                      <span className="text-gray-600">Currency:</span>
                                      <span className="font-medium text-gray-900">{recWithPlatform.currency}</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>

                            {/* Platform Recommendation Section - Enhanced */}
                            {recWithPlatform.platform_recommendation ? (
                              <div className="mt-4 pt-4 border-t-2 border-purple-200">
                                <div className="bg-gradient-to-r from-purple-100 to-blue-100 border-2 border-purple-300 rounded-xl p-6 shadow-lg">
                                  <div className="flex items-center mb-4">
                                    <div className="bg-purple-200 p-3 rounded-xl mr-4">
                                      <MessageCircle className="h-8 w-8 text-purple-700" />
                                    </div>
                                    <div>
                                      <h4 className="text-xl font-bold text-purple-900 mb-1">
                                        🏦 WIO Bank Platform
                                      </h4>
                                      <h5 className="text-lg font-semibold text-purple-800">
                                        {recWithPlatform.platform_recommendation.app_name || recWithPlatform.platform_recommendation.platform_name}
                                      </h5>
                                      <p className="text-sm text-purple-700 font-medium">
                                        {recWithPlatform.platform_recommendation.platform_type}
                                      </p>
                                    </div>
                                  </div>

                                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                    {/* Features */}
                                    <div>
                                      <h6 className="font-semibold text-purple-900 mb-2 flex items-center">
                                        <CheckCircle className="h-4 w-4 mr-1" />
                                        Key Features
                                      </h6>
                                      <ul className="text-sm text-purple-700 space-y-1">
                                        {recWithPlatform.platform_recommendation.features.map((feature, idx) => (
                                          <li key={idx} className="flex items-start">
                                            <span className="text-purple-500 mr-2">•</span>
                                            {feature}
                                          </li>
                                        ))}
                                      </ul>
                                    </div>

                                    {/* Setup Steps */}
                                    <div>
                                      <h6 className="font-semibold text-purple-900 mb-2 flex items-center">
                                        <Target className="h-4 w-4 mr-1" />
                                        Getting Started
                                      </h6>
                                      <ol className="text-sm text-purple-700 space-y-1">
                                        {recWithPlatform.platform_recommendation.setup_steps.map((step, idx) => (
                                          <li key={idx} className="flex items-start">
                                            <span className="bg-purple-200 text-purple-800 rounded-full w-4 h-4 flex items-center justify-center text-xs font-bold mr-2 mt-0.5 flex-shrink-0">
                                              {idx + 1}
                                            </span>
                                            {step}
                                          </li>
                                        ))}
                                      </ol>
                                    </div>

                                    {/* Benefits */}
                                    <div>
                                      <h6 className="font-semibold text-purple-900 mb-2 flex items-center">
                                        <TrendingUp className="h-4 w-4 mr-1" />
                                        Benefits
                                      </h6>
                                      <ul className="text-sm text-purple-700 space-y-1">
                                        {recWithPlatform.platform_recommendation.benefits.map((benefit, idx) => (
                                          <li key={idx} className="flex items-start">
                                            <span className="text-purple-500 mr-2">•</span>
                                            {benefit}
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            ) : (
                              <div className="mt-4 pt-4 border-t border-gray-200">
                                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                                  <p className="text-yellow-800 text-sm">
                                    <strong>Note:</strong> Platform recommendation not available for this instrument.
                                  </p>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                      </div>
                    </div>
                  ));
                })()}
              </div>
            )}

            {/* Analysis Tab */}
            {activeTab === 'analysis' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Risk vs Return Analysis</h3>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={barData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Bar yAxisId="left" dataKey="risk" fill="#8884d8" name="Risk Level" />
                      <Bar yAxisId="right" dataKey="return" fill="#82ca9d" name="Expected Return %" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
                    <div className="flex items-center mb-4">
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center mr-3">
                        <span className="text-white text-sm font-bold">📊</span>
                      </div>
                      <h4 className="font-bold text-gray-900 text-lg">Risk Assessment</h4>
                    </div>

                    {typeof plan.risk_assessment === 'string' ? (
                      // Parse **String:** patterns into bullet points
                      (() => {
                        const riskText = plan.risk_assessment;

                        // Parse **String:** patterns and create bullet points
                        const bulletPoints: string[] = [];

                        // Split by **String:** pattern and process each section
                        const sections = riskText.split(/\*\*([^*]+):\*\*/);

                        for (let i = 1; i < sections.length; i += 2) {
                          const label = sections[i].trim();
                          const content = sections[i + 1] ? sections[i + 1].trim() : '';

                          if (content) {
                            // Clean up the content
                            let cleanContent = content
                              .replace(/^\s*\*\s*/, '') // Remove leading asterisk
                              .replace(/\s*\*+\s*$/, '') // Remove trailing asterisks
                              .replace(/\s*\*\*.*$/, '') // Remove trailing **String:** patterns
                              .replace(/\.$/, '') // Remove trailing period
                              .trim();

                            // Split content at sentence boundaries if it's too long
                            if (cleanContent.length > 150) {
                              const sentences = cleanContent.split(/\.\s+/);
                              sentences.forEach(sentence => {
                                if (sentence.trim().length > 10) {
                                  bulletPoints.push(`${label}: ${sentence.trim()}`);
                                }
                              });
                            } else if (cleanContent.length > 10) {
                              bulletPoints.push(`${label}: ${cleanContent}`);
                            }
                          }
                        }

                        // If no **String:** patterns found, try alternative parsing
                        if (bulletPoints.length === 0) {
                          // Look for patterns like "Risk Level: value" without markdown
                          const patterns = [
                            /Risk Level[:\s]*([^.\n]+)/i,
                            /Description[:\s]*([^.\n]+)/i,
                            /Suitability[:\s]*([^.\n]+)/i,
                            /Mitigation[:\s]*([^.\n]+)/i,
                            /Allocation[:\s]*([^.\n]+)/i,
                            /Strategy[:\s]*([^.\n]+)/i
                          ];

                          patterns.forEach(pattern => {
                            const match = riskText.match(pattern);
                            if (match && match[1]) {
                              const label = pattern.source.split('[')[0];
                              const content = match[1].trim().replace(/[.*]/g, '');
                              if (content.length > 10) {
                                bulletPoints.push(`${label}: ${content}`);
                              }
                            }
                          });
                        }

                        // If still no points, create from sentences
                        if (bulletPoints.length === 0) {
                          const sentences = riskText.split(/[.!?]+/).filter(s => s.trim().length > 20);
                          sentences.slice(0, 4).forEach((sentence, index) => {
                            const cleaned = sentence.trim().replace(/[*#]/g, '');
                            if (cleaned.length > 10) {
                              bulletPoints.push(`Point ${index + 1}: ${cleaned}`);
                            }
                          });
                        }

                        return (
                          <div className="space-y-4">
                            {/* Simple Bullet Points Display */}
                            <div className="bg-white rounded-lg p-4 border border-blue-100">
                              <div className="flex items-start space-x-3">
                                <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-blue-600 text-xs">📊</span>
                                </div>
                                <div className="flex-1">
                                  <h5 className="font-semibold text-gray-900 mb-2">Risk Assessment Details</h5>
                                  {bulletPoints.length > 0 ? (
                                    <ul className="space-y-2">
                                      {bulletPoints.map((point: string, index: number) => (
                                        <li key={index} className="text-gray-700 text-sm flex items-start">
                                          <span className="text-blue-500 mr-2 flex-shrink-0 mt-1">•</span>
                                          <span className="leading-relaxed">{point}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <p className="text-gray-700 text-sm">{riskText}</p>
                                  )}
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      })()
                    ) : (
                      // Structured object format
                      <div className="space-y-4">
                        {/* Risk Level Badge */}
                        <div className="flex items-center space-x-3">
                          <div className="bg-blue-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                            {plan.risk_assessment.risk_level || 'Moderate Risk'}
                          </div>
                          <div className="flex-1 h-2 bg-gray-200 rounded-full">
                            <div className="h-2 bg-gradient-to-r from-green-400 to-blue-500 rounded-full" style={{width: '60%'}}></div>
                          </div>
                        </div>

                        {/* Information Cards */}
                        <div className="grid grid-cols-1 gap-3">
                          <div className="bg-white rounded-lg p-4 border border-blue-100">
                            <div className="flex items-start space-x-3">
                              <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                <span className="text-blue-600 text-xs">ℹ️</span>
                              </div>
                              <div>
                                <h5 className="font-semibold text-gray-900 mb-1">Description</h5>
                                <p className="text-gray-700 text-sm">{plan.risk_assessment.description}</p>
                              </div>
                            </div>
                          </div>

                          {plan.risk_assessment.suitability && (
                            <div className="bg-white rounded-lg p-4 border border-green-100">
                              <div className="flex items-start space-x-3">
                                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-green-600 text-xs">✓</span>
                                </div>
                                <div>
                                  <h5 className="font-semibold text-gray-900 mb-1">Suitable For</h5>
                                  <p className="text-gray-700 text-sm">{plan.risk_assessment.suitability}</p>
                                </div>
                              </div>
                            </div>
                          )}

                          {plan.risk_assessment.recommended_allocation && (
                            <div className="bg-white rounded-lg p-4 border border-purple-100">
                              <div className="flex items-start space-x-3">
                                <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-purple-600 text-xs">🎯</span>
                                </div>
                                <div>
                                  <h5 className="font-semibold text-gray-900 mb-1">Allocation Focus</h5>
                                  <p className="text-gray-700 text-sm">{plan.risk_assessment.recommended_allocation}</p>
                                </div>
                              </div>
                            </div>
                          )}

                          {plan.risk_assessment.time_factor && (
                            <div className="bg-white rounded-lg p-4 border border-indigo-100">
                              <div className="flex items-start space-x-3">
                                <div className="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-indigo-600 text-xs">⏰</span>
                                </div>
                                <div>
                                  <h5 className="font-semibold text-gray-900 mb-1">Time Considerations</h5>
                                  <p className="text-gray-700 text-sm">{plan.risk_assessment.time_factor}</p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="bg-gradient-to-br from-green-50 to-teal-50 rounded-lg p-6 border border-green-200">
                    <div className="flex items-center mb-4">
                      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center mr-3">
                        <span className="text-white text-sm font-bold">⏰</span>
                      </div>
                      <h4 className="font-bold text-gray-900 text-lg">Time Horizon Analysis</h4>
                    </div>

                    {typeof plan.time_horizon_analysis === 'string' ? (
                      // Parse string format into structured display
                      (() => {
                        const timeText = plan.time_horizon_analysis;

                        // Clean up markdown formatting
                        const cleanTimeText = timeText
                          .replace(/\*\*/g, '') // Remove bold markdown
                          .replace(/\*/g, '') // Remove asterisks
                          .replace(/#{1,6}\s/g, '') // Remove headers
                          .trim();

                        // Extract timeline with better pattern matching
                        const timelineMatch = cleanTimeText.match(/(?:Timeline|Horizon)[:\s]*([^.*\n]+?)(?:\.|$)/i);
                        const timeline = timelineMatch ? timelineMatch[1].trim().replace(/[.*]/g, '') : 'Long-term (30 years)';

                        // Extract strategy with better pattern matching
                        const strategyMatch = cleanTimeText.match(/Strategy[:\s]*([^.*\n]+?)(?:\.|Short-Term|Medium-Term|Long-Term|$)/i);
                        let strategy = strategyMatch ? strategyMatch[1].trim().replace(/[.*]/g, '') : '';

                        // If no strategy found, extract from the beginning
                        if (!strategy) {
                          const firstSentence = cleanTimeText.split(/[.!?]+/)[0];
                          strategy = firstSentence.length > 20 ? firstSentence : 'Long-term investment approach with periodic rebalancing';
                        }

                        // Extract phase-specific information
                        const shortTermMatch = cleanTimeText.match(/Short-Term[^:]*:[^*]*?([^.*\n]+?)(?:\.|Medium-Term|$)/i);
                        const shortTerm = shortTermMatch ? shortTermMatch[1].trim().replace(/[.*]/g, '') : '';

                        const mediumTermMatch = cleanTimeText.match(/Medium-Term[^:]*:[^*]*?([^.*\n]+?)(?:\.|Long-Term|$)/i);
                        const mediumTerm = mediumTermMatch ? mediumTermMatch[1].trim().replace(/[.*]/g, '') : '';

                        const longTermMatch = cleanTimeText.match(/Long-Term[^:]*:[^*]*?([^.*\n]+?)(?:\.|MONTHLY|$)/i);
                        const longTerm = longTermMatch ? longTermMatch[1].trim().replace(/[.*]/g, '') : '';

                        // Extract bullet points and key information
                        const timeKeyPoints: string[] = [];

                        // Look for explicit bullet points
                        const bulletMatches = cleanTimeText.match(/(?:^|\n)\s*[-•*]\s*([^.\n]+)/gm);
                        if (bulletMatches) {
                          bulletMatches.forEach(match => {
                            const point = match.replace(/^[\n\s]*[-•*]\s*/, '').trim();
                            if (point.length > 10) {
                              timeKeyPoints.push(point);
                            }
                          });
                        }

                        // If no bullet points found, extract key sentences
                        if (timeKeyPoints.length === 0) {
                          const sentences = cleanTimeText.split(/[.!?]+/).filter(s => {
                            const trimmed = s.trim();
                            return trimmed.length > 15 &&
                                   !trimmed.toLowerCase().includes('timeline') &&
                                   !trimmed.toLowerCase().includes('strategy');
                          });

                          sentences.slice(0, 3).forEach(sentence => {
                            const cleaned = sentence.trim().replace(/[.*]/g, '');
                            if (cleaned.length > 10) {
                              timeKeyPoints.push(cleaned);
                            }
                          });
                        }

                        return (
                          <div className="space-y-4">
                            {/* Timeline Badge */}
                            <div className="flex items-center space-x-3">
                              <div className="bg-green-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                                {timeline}
                              </div>
                              <div className="flex-1">
                                <div className="flex justify-between text-xs text-gray-500 mb-1">
                                  <span>Start</span>
                                  <span>Mid-term</span>
                                  <span>Retirement</span>
                                </div>
                                <div className="h-2 bg-gray-200 rounded-full">
                                  <div className="h-2 bg-gradient-to-r from-green-400 via-yellow-400 to-blue-500 rounded-full" style={{width: '100%'}}></div>
                                </div>
                              </div>
                            </div>

                            {/* Strategy and Key Points */}
                            <div className="grid grid-cols-1 gap-3">
                              <div className="bg-white rounded-lg p-4 border border-green-100">
                                <div className="flex items-start space-x-3">
                                  <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                    <span className="text-green-600 text-xs">📈</span>
                                  </div>
                                  <div>
                                    <h5 className="font-semibold text-gray-900 mb-1">Investment Strategy</h5>
                                    <p className="text-gray-700 text-sm">{strategy}</p>
                                  </div>
                                </div>
                              </div>

                              {/* Timeline Phases */}
                              <div className="bg-white rounded-lg p-4 border border-teal-100">
                                <div className="flex items-start space-x-3">
                                  <div className="w-6 h-6 bg-teal-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                    <span className="text-teal-600 text-xs">🎯</span>
                                  </div>
                                  <div className="flex-1">
                                    <h5 className="font-semibold text-gray-900 mb-2">Investment Phases</h5>
                                    <div className="space-y-2">
                                      <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                                        <span className="text-sm text-gray-700">Years 1-10: Growth Phase</span>
                                      </div>
                                      <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                                        <span className="text-sm text-gray-700">Years 11-20: Consolidation Phase</span>
                                      </div>
                                      <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
                                        <span className="text-sm text-gray-700">Years 21-30: Pre-retirement Phase</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>

                              {/* Key Considerations */}
                              {timeKeyPoints.length > 0 && (
                                <div className="bg-white rounded-lg p-4 border border-blue-100">
                                  <div className="flex items-start space-x-3">
                                    <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                      <span className="text-blue-600 text-xs">💡</span>
                                    </div>
                                    <div className="flex-1">
                                      <h5 className="font-semibold text-gray-900 mb-2">Key Considerations</h5>
                                      <ul className="space-y-1">
                                        {timeKeyPoints.map((point: string, index: number) => (
                                          <li key={index} className="text-gray-700 text-sm flex items-start">
                                            <span className="text-blue-500 mr-2 flex-shrink-0">•</span>
                                            <span>{point}</span>
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  </div>
                                </div>
                              )}

                              {/* Phase-specific Information */}
                              {(shortTerm || mediumTerm || longTerm) && (
                                <div className="bg-white rounded-lg p-4 border border-teal-100">
                                  <div className="flex items-start space-x-3">
                                    <div className="w-6 h-6 bg-teal-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                      <span className="text-teal-600 text-xs">📅</span>
                                    </div>
                                    <div className="flex-1">
                                      <h5 className="font-semibold text-gray-900 mb-2">Phase-Specific Strategy</h5>
                                      <div className="space-y-2">
                                        {shortTerm && (
                                          <div className="flex items-start space-x-3">
                                            <div className="w-3 h-3 bg-green-400 rounded-full mt-1.5 flex-shrink-0"></div>
                                            <div>
                                              <div className="text-sm font-medium text-gray-900">Short-term Focus</div>
                                              <div className="text-sm text-gray-700">{shortTerm}</div>
                                            </div>
                                          </div>
                                        )}
                                        {mediumTerm && (
                                          <div className="flex items-start space-x-3">
                                            <div className="w-3 h-3 bg-yellow-400 rounded-full mt-1.5 flex-shrink-0"></div>
                                            <div>
                                              <div className="text-sm font-medium text-gray-900">Medium-term Focus</div>
                                              <div className="text-sm text-gray-700">{mediumTerm}</div>
                                            </div>
                                          </div>
                                        )}
                                        {longTerm && (
                                          <div className="flex items-start space-x-3">
                                            <div className="w-3 h-3 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
                                            <div>
                                              <div className="text-sm font-medium text-gray-900">Long-term Focus</div>
                                              <div className="text-sm text-gray-700">{longTerm}</div>
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })()
                    ) : (
                      // Structured object format
                      <div className="space-y-4">
                        {/* Timeline Badge */}
                        <div className="flex items-center space-x-3">
                          <div className="bg-green-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                            {plan.time_horizon_analysis.horizon_category || 'Long-term'}
                          </div>
                          <div className="flex-1">
                            <div className="flex justify-between text-xs text-gray-500 mb-1">
                              <span>Start</span>
                              <span>Mid-term</span>
                              <span>Retirement</span>
                            </div>
                            <div className="h-2 bg-gray-200 rounded-full">
                              <div className="h-2 bg-gradient-to-r from-green-400 via-yellow-400 to-blue-500 rounded-full" style={{width: '100%'}}></div>
                            </div>
                          </div>
                        </div>

                        {/* Information Cards */}
                        <div className="grid grid-cols-1 gap-3">
                          {plan.time_horizon_analysis.strategy && (
                            <div className="bg-white rounded-lg p-4 border border-green-100">
                              <div className="flex items-start space-x-3">
                                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-green-600 text-xs">📈</span>
                                </div>
                                <div>
                                  <h5 className="font-semibold text-gray-900 mb-1">Investment Strategy</h5>
                                  <p className="text-gray-700 text-sm">{plan.time_horizon_analysis.strategy}</p>
                                </div>
                              </div>
                            </div>
                          )}

                          {plan.time_horizon_analysis.flexibility && (
                            <div className="bg-white rounded-lg p-4 border border-yellow-100">
                              <div className="flex items-start space-x-3">
                                <div className="w-6 h-6 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-yellow-600 text-xs">🔄</span>
                                </div>
                                <div>
                                  <h5 className="font-semibold text-gray-900 mb-1">Flexibility</h5>
                                  <p className="text-gray-700 text-sm">{plan.time_horizon_analysis.flexibility}</p>
                                </div>
                              </div>
                            </div>
                          )}

                          {plan.time_horizon_analysis.milestones && (
                            <div className="bg-white rounded-lg p-4 border border-teal-100">
                              <div className="flex items-start space-x-3">
                                <div className="w-6 h-6 bg-teal-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-teal-600 text-xs">🎯</span>
                                </div>
                                <div className="flex-1">
                                  <h5 className="font-semibold text-gray-900 mb-2">Investment Milestones</h5>
                                  <div className="space-y-2">
                                    {plan.time_horizon_analysis.milestones.short_term && (
                                      <div className="flex items-start space-x-3">
                                        <div className="w-3 h-3 bg-green-400 rounded-full mt-1.5 flex-shrink-0"></div>
                                        <div>
                                          <div className="text-sm font-medium text-gray-900">Short-term (1-5 years)</div>
                                          <div className="text-sm text-gray-700">{plan.time_horizon_analysis.milestones.short_term}</div>
                                        </div>
                                      </div>
                                    )}
                                    {plan.time_horizon_analysis.milestones.medium_term && (
                                      <div className="flex items-start space-x-3">
                                        <div className="w-3 h-3 bg-yellow-400 rounded-full mt-1.5 flex-shrink-0"></div>
                                        <div>
                                          <div className="text-sm font-medium text-gray-900">Medium-term (6-15 years)</div>
                                          <div className="text-sm text-gray-700">{plan.time_horizon_analysis.milestones.medium_term}</div>
                                        </div>
                                      </div>
                                    )}
                                    {plan.time_horizon_analysis.milestones.long_term && (
                                      <div className="flex items-start space-x-3">
                                        <div className="w-3 h-3 bg-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
                                        <div>
                                          <div className="text-sm font-medium text-gray-900">Long-term (16+ years)</div>
                                          <div className="text-sm text-gray-700">{plan.time_horizon_analysis.milestones.long_term}</div>
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          )}

                          {plan.time_horizon_analysis.retirement_readiness && (
                            <div className="bg-white rounded-lg p-4 border border-purple-100">
                              <div className="flex items-start space-x-3">
                                <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                                  <span className="text-purple-600 text-xs">🏖️</span>
                                </div>
                                <div>
                                  <h5 className="font-semibold text-gray-900 mb-1">Retirement Readiness</h5>
                                  <p className="text-gray-700 text-sm">{plan.time_horizon_analysis.retirement_readiness}</p>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
                    <AlertCircle className="h-5 w-5 mr-2" />
                    Compliance Notes
                  </h4>
                  <p className="text-blue-800">{plan.compliance_notes}</p>
                </div>
              </div>
            )}

            {/* Goals Tab */}
            {activeTab === 'goals' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Investment Goals Timeline & Risk Analysis</h3>
                  <div className="space-y-4">
                    {Object.entries(plan.goal_achievement_timeline).map(([goal, years]) => {
                      // Goal categorization logic with dynamic risk data
                      const getGoalInfo = (goalName: string, timelineYears: number) => {
                        const name = goalName.toLowerCase();

                        // Get dynamic risks and mitigation from API response
                        const dynamicData = plan.goal_risks_mitigation?.[goalName] || plan.goal_risks_mitigation?.[goal];

                        if (name.includes('retirement')) {
                          return {
                            category: 'Long-term',
                            icon: '🏖️',
                            bgColor: 'bg-blue-50',
                            borderColor: 'border-blue-500',
                            textColor: 'text-blue-600',
                            priority: 'High',
                            description: 'Primary retirement planning goal',
                            risks: dynamicData?.risks || ['Market volatility over long term', 'Inflation impact', 'Sequence of returns risk'],
                            workarounds: dynamicData?.mitigation || ['Diversified portfolio', 'Regular rebalancing', 'Inflation-protected securities']
                          };
                        } else if (name.includes('house') || name.includes('property')) {
                          return {
                            category: 'Medium-term',
                            icon: '🏠',
                            bgColor: 'bg-green-50',
                            borderColor: 'border-green-500',
                            textColor: 'text-green-600',
                            priority: 'High',
                            description: 'Real estate acquisition goal',
                            risks: dynamicData?.risks || ['Property market fluctuations', 'Interest rate changes', 'Down payment timing'],
                            workarounds: dynamicData?.mitigation || ['Conservative allocation closer to target', 'Fixed income instruments', 'Market timing flexibility']
                          };
                        } else if (name.includes('education')) {
                          return {
                            category: 'Medium-term',
                            icon: '🎓',
                            bgColor: 'bg-purple-50',
                            borderColor: 'border-purple-500',
                            textColor: 'text-purple-600',
                            priority: 'High',
                            description: 'Education funding goal',
                            risks: dynamicData?.risks || ['Education cost inflation', 'Fixed timeline', 'Currency fluctuations'],
                            workarounds: dynamicData?.mitigation || ['Education-specific savings plans', 'Conservative approach near deadline', 'Scholarship opportunities']
                          };
                        } else if (name.includes('travel')) {
                          return {
                            category: 'Short-term',
                            icon: '✈️',
                            bgColor: 'bg-orange-50',
                            borderColor: 'border-orange-500',
                            textColor: 'text-orange-600',
                            priority: 'Medium',
                            description: 'Travel and leisure goal',
                            risks: dynamicData?.risks || ['Currency fluctuations', 'Economic disruptions', 'Travel restrictions'],
                            workarounds: dynamicData?.mitigation || ['Liquid savings', 'Flexible timing', 'Currency hedging']
                          };
                        } else if (name.includes('wealth') || name.includes('building')) {
                          return {
                            category: 'Long-term',
                            icon: '💰',
                            bgColor: 'bg-indigo-50',
                            borderColor: 'border-indigo-500',
                            textColor: 'text-indigo-600',
                            priority: 'Medium',
                            description: 'Wealth accumulation goal',
                            risks: dynamicData?.risks || ['Market cycles', 'Sequence of returns risk', 'Lifestyle inflation'],
                            workarounds: dynamicData?.mitigation || ['Dollar-cost averaging', 'Diversification', 'Long-term perspective']
                          };
                        } else if (name.includes('emergency')) {
                          return {
                            category: 'Critical',
                            icon: '🛡️',
                            bgColor: 'bg-red-50',
                            borderColor: 'border-red-500',
                            textColor: 'text-red-600',
                            priority: 'Critical',
                            description: 'Emergency fund safety net',
                            risks: dynamicData?.risks || ['Inflation erosion', 'Opportunity cost', 'Insufficient coverage'],
                            workarounds: dynamicData?.mitigation || ['High-yield savings', 'Money market funds', 'Laddered CDs']
                          };
                        } else {
                          return {
                            category: timelineYears <= 5 ? 'Short-term' : timelineYears <= 15 ? 'Medium-term' : 'Long-term',
                            icon: '🎯',
                            bgColor: 'bg-gray-50',
                            borderColor: 'border-gray-500',
                            textColor: 'text-gray-600',
                            priority: 'Medium',
                            description: 'General financial goal',
                            risks: dynamicData?.risks || ['Market uncertainty', 'Timeline constraints', 'Goal clarity'],
                            workarounds: dynamicData?.mitigation || ['Balanced approach', 'Regular monitoring', 'Flexible strategy']
                          };
                        }
                      };

                      const goalInfo = getGoalInfo(goal, years);

                      return (
                        <div key={goal} className={`border-l-4 ${goalInfo.borderColor} ${goalInfo.bgColor} rounded-lg p-4`}>
                          <div className="flex items-center justify-between cursor-pointer"
                               onClick={() => setExpandedRecommendations(prev => {
                                 const newSet = new Set(prev);
                                 if (newSet.has(goal)) {
                                   newSet.delete(goal);
                                 } else {
                                   newSet.add(goal);
                                 }
                                 return newSet;
                               })}>
                            <div className="flex items-center">
                              <span className="text-2xl mr-3">{goalInfo.icon}</span>
                              <div>
                                <h4 className="font-semibold capitalize text-gray-900 flex items-center">
                                  {goal.replace('_', ' ')}
                                  <span className={`ml-2 px-2 py-1 text-xs rounded-full ${goalInfo.bgColor} ${goalInfo.textColor} border`}>
                                    {goalInfo.category}
                                  </span>
                                  <span className={`ml-2 px-2 py-1 text-xs rounded-full ${
                                    goalInfo.priority === 'Critical' ? 'bg-red-100 text-red-800' :
                                    goalInfo.priority === 'High' ? 'bg-orange-100 text-orange-800' :
                                    'bg-gray-100 text-gray-800'
                                  }`}>
                                    {goalInfo.priority} Priority
                                  </span>
                                </h4>
                                <p className="text-sm text-gray-600">{goalInfo.description}</p>
                              </div>
                            </div>
                            <div className="text-right flex items-center">
                              <div>
                                <div className={`text-2xl font-bold ${goalInfo.textColor}`}>{years}</div>
                                <div className="text-sm text-gray-500">years</div>
                              </div>
                              {expandedRecommendations.has(goal) ? <ChevronUp className="ml-2 h-5 w-5" /> : <ChevronDown className="ml-2 h-5 w-5" />}
                            </div>
                          </div>

                          {expandedRecommendations.has(goal) && (
                            <div className="mt-4 pt-4 border-t border-gray-200">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                  <h5 className="font-semibold text-red-700 mb-2 flex items-center">
                                    <AlertCircle className="h-4 w-4 mr-1" />
                                    Potential Risks & Challenges
                                  </h5>
                                  <ul className="text-sm text-red-600 space-y-1">
                                    {(() => {
                                      // Use dynamic data if available, otherwise fall back to static
                                      const dynamicRisks = plan.goal_risks_mitigation?.[goal]?.risks;
                                      const risks = dynamicRisks && dynamicRisks.length > 0 ? dynamicRisks : goalInfo.risks;

                                      return risks.map((risk, index) => (
                                        <li key={index} className="flex items-start">
                                          <span className="text-red-500 mr-2">•</span>
                                          {risk}
                                        </li>
                                      ));
                                    })()}
                                  </ul>
                                </div>
                                <div>
                                  <h5 className="font-semibold text-green-700 mb-2 flex items-center">
                                    <CheckCircle className="h-4 w-4 mr-1" />
                                    Mitigation Strategies
                                  </h5>
                                  <ul className="text-sm text-green-600 space-y-1">
                                    {(() => {
                                      // Use dynamic data if available, otherwise fall back to static
                                      const dynamicMitigation = plan.goal_risks_mitigation?.[goal]?.mitigation;
                                      const mitigation = dynamicMitigation && dynamicMitigation.length > 0 ? dynamicMitigation : goalInfo.workarounds;

                                      return mitigation.map((strategy, index) => (
                                        <li key={index} className="flex items-start">
                                          <span className="text-green-500 mr-2">•</span>
                                          {strategy}
                                        </li>
                                      ));
                                    })()}
                                  </ul>
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold mb-4">Additional Financial Advice</h3>
                  <div className="space-y-3">
                    {plan.additional_advice.map((advice, index) => (
                      <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                        <CheckCircle className="h-5 w-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                        <p className="text-green-800">{advice}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-semibold text-yellow-900 mb-2 flex items-center">
                    <Clock className="h-5 w-5 mr-2" />
                    Monthly Savings Required
                  </h4>
                  <p className="text-yellow-800">
                    To achieve your financial goals, continue investing{' '}
                    <span className="font-bold">
                      {typeof plan.monthly_savings_needed === 'number'
                        ? formatCurrency(plan.monthly_savings_needed)
                        : plan.monthly_savings_needed
                      }
                    </span> per month.
                  </p>
                </div>
              </div>
            )}

            {/* Details Tab - LLM Response Sections */}
            {activeTab === 'details' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <Info className="h-5 w-5 mr-2 text-blue-600" />
                    Detailed Financial Plan Analysis
                  </h3>

                  {plan.raw_llm_response ? (
                    <div className="space-y-6">
                      {/* Parse and display LLM response sections */}
                      {/* {(() => {
                        const sections = parseLLMResponseSections(plan.raw_llm_response);
                        return Object.entries(sections).map(([sectionName, content]) => (
                          <div key={sectionName} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
                            <h4 className="font-semibold text-gray-900 mb-3 text-lg border-b border-gray-200 pb-2">
                              {sectionName.replace(/_/g, ' ')}
                            </h4>
                            <div className="prose prose-sm max-w-none">
                              <div className="text-gray-700 whitespace-pre-line leading-relaxed">
                                {content}
                              </div>
                            </div>
                          </div>
                        ));
                      })()} */}

                      {/* Evaluation Metadata (if available) */}
                      {plan.evaluation_metadata && (
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
                          <h4 className="font-semibold text-blue-900 mb-3">AI Evaluation Summary</h4>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                              <span className="text-sm text-blue-700">Evaluator:</span>
                              <span className="ml-2 font-semibold text-blue-900">
                                {plan.evaluation_metadata.evaluator_used ? 'Gemini 2.5 Pro' : 'Not Used'}
                              </span>
                            </div>
                            <div>
                              <span className="text-sm text-blue-700">Quality Score:</span>
                              <span className="ml-2 font-semibold text-blue-900">
                                {plan.evaluation_metadata.original_score?.toFixed(1) || 'N/A'}/10
                              </span>
                            </div>
                            <div>
                              <span className="text-sm text-blue-700">Improved:</span>
                              <span className={`ml-2 px-2 py-1 rounded text-xs font-medium ${
                                plan.evaluation_metadata.improvement_applied
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-gray-100 text-gray-800'
                              }`}>
                                {plan.evaluation_metadata.improvement_applied ? 'Yes' : 'No'}
                              </span>
                            </div>
                          </div>
                        </div>
                      )}


                    </div>
                  ) : (
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
                      <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                      <h4 className="font-medium text-gray-900 mb-2">No Evaluation Data Available</h4>
                      <p className="text-gray-600">
                        Evaluation metadata is not available for this financial plan.
                        This may occur if the evaluator agent was not active during plan generation.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer Summary */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Portfolio Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className="text-2xl font-bold text-blue-600">{plan.recommendations.length}</div>
                <div className="text-sm text-gray-500">Investment Instruments</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(plan.recommendations.reduce((sum, rec) => sum + rec.investment_amount, 0))}
                </div>
                <div className="text-sm text-gray-500">Total Monthly Investment</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">{formatPercentage(plan.expected_portfolio_return)}</div>
                <div className="text-sm text-gray-500">Expected Annual Return</div>
              </div>
            </div>
          </div>
        </div>

        {/* Feedback System for Reinforcement Learning */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <FeedbackSystem
            query={JSON.stringify(plan.user_profile)}
            response={JSON.stringify(plan)}
            userProfile={plan.user_profile}
            sessionId={plan.response_metadata?.session_id}
            userId={plan.response_metadata?.user_id}
            onFeedbackSubmitted={(success) => {
              if (success) {
                console.log('Feedback submitted successfully');
              }
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default FinancialPlannerDashboard;