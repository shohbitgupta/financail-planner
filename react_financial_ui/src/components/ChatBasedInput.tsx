import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, CheckCircle, ArrowRight } from 'lucide-react';

interface ChatMessage {
  id: string;
  type: 'bot' | 'user';
  content: string;
  timestamp: Date;
}

interface UserData {
  age?: number;
  retirement_age?: number;
  annual_salary?: number;
  annual_expenses?: number;
  current_savings?: number;
  risk_tolerance?: string;
  goals?: string[];
  is_sharia_compliant?: boolean;
  preferred_market?: string;
  currency?: string;
}

interface ChatBasedInputProps {
  onComplete: (userData: UserData) => void;
  onCancel: () => void;
}

const ChatBasedInput: React.FC<ChatBasedInputProps> = ({ onComplete, onCancel }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentInput, setCurrentInput] = useState('');
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userData, setUserData] = useState<UserData>({});
  const [isCompleted, setIsCompleted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const questions = [
    {
      key: 'age',
      question: "Hi! I'm your AI Financial Planner. Let's start by getting to know you better. What's your current age?",
      type: 'number',
      validation: (value: string) => {
        const num = parseInt(value);
        return num >= 18 && num <= 100 ? null : "Please enter a valid age between 18 and 100.";
      }
    },
    {
      key: 'retirement_age',
      question: "Great! At what age would you like to retire?",
      type: 'number',
      validation: (value: string, userData: UserData) => {
        const num = parseInt(value);
        const currentAge = userData.age || 0;
        return num > currentAge && num <= 100 ? null : `Please enter a retirement age greater than ${currentAge} and less than 100.`;
      }
    },
    {
      key: 'annual_salary',
      question: "What's your current annual salary? (Please enter the amount in your local currency)",
      type: 'number',
      validation: (value: string) => {
        const num = parseFloat(value);
        return num > 0 ? null : "Please enter a valid salary amount.";
      }
    },
    {
      key: 'annual_expenses',
      question: "What are your approximate annual expenses? (Include housing, food, transportation, etc.)",
      type: 'number',
      validation: (value: string) => {
        const num = parseFloat(value);
        return num > 0 ? null : "Please enter a valid expense amount.";
      }
    },
    {
      key: 'current_savings',
      question: "How much do you currently have in savings and investments?",
      type: 'number',
      validation: (value: string) => {
        const num = parseFloat(value);
        return num >= 0 ? null : "Please enter a valid savings amount (can be 0).";
      }
    },
    {
      key: 'risk_tolerance',
      question: "What's your investment risk tolerance? Please choose one:\n\n1. Conservative (Low risk, stable returns)\n2. Moderate (Balanced risk and return)\n3. Aggressive (High risk, high potential returns)",
      type: 'choice',
      choices: ['conservative', 'moderate', 'aggressive'],
      validation: (value: string) => {
        const choice = value.toLowerCase();
        if (choice.includes('1') || choice.includes('conservative')) return null;
        if (choice.includes('2') || choice.includes('moderate')) return null;
        if (choice.includes('3') || choice.includes('aggressive')) return null;
        return "Please choose 1 (Conservative), 2 (Moderate), or 3 (Aggressive).";
      }
    },
    {
      key: 'goals',
      question: "What are your main financial goals? You can mention multiple goals like:\n- Retirement planning\n- Buying a house\n- Children's education\n- Emergency fund\n- Travel\n- Starting a business",
      type: 'text',
      validation: (value: string) => {
        return value.trim().length > 0 ? null : "Please tell us about your financial goals.";
      }
    },
    {
      key: 'is_sharia_compliant',
      question: "Do you require Sharia-compliant (Islamic) investments?\n\n1. Yes, only Sharia-compliant investments\n2. No, conventional investments are fine",
      type: 'boolean',
      validation: (value: string) => {
        const choice = value.toLowerCase();
        if (choice.includes('1') || choice.includes('yes') || choice.includes('sharia')) return null;
        if (choice.includes('2') || choice.includes('no') || choice.includes('conventional')) return null;
        return "Please choose 1 (Yes) or 2 (No).";
      }
    },
    {
      key: 'preferred_market',
      question: "Which market would you prefer to invest in?\n\n1. UAE Market\n2. US Market\n3. Both UAE and US Markets",
      type: 'choice',
      choices: ['UAE', 'US', 'Both'],
      validation: (value: string) => {
        const choice = value.toLowerCase();
        if (choice.includes('1') || choice.includes('uae')) return null;
        if (choice.includes('2') || choice.includes('us') || choice.includes('usa')) return null;
        if (choice.includes('3') || choice.includes('both')) return null;
        return "Please choose 1 (UAE), 2 (US), or 3 (Both).";
      }
    },
    {
      key: 'currency',
      question: "What currency should we use for your financial plan?\n\n1. USD (US Dollars)\n2. AED (UAE Dirhams)",
      type: 'choice',
      choices: ['USD', 'AED'],
      validation: (value: string) => {
        const choice = value.toLowerCase();
        if (choice.includes('1') || choice.includes('usd') || choice.includes('dollar')) return null;
        if (choice.includes('2') || choice.includes('aed') || choice.includes('dirham')) return null;
        return "Please choose 1 (USD) or 2 (AED).";
      }
    }
  ];

  useEffect(() => {
    // Start the conversation
    if (messages.length === 0) {
      addBotMessage(questions[0].question);
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addBotMessage = (content: string) => {
    const message: ChatMessage = {
      id: Date.now().toString(),
      type: 'bot',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const addUserMessage = (content: string) => {
    const message: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const processUserInput = (input: string) => {
    const currentQuestion = questions[currentQuestionIndex];
    const validation = currentQuestion.validation(input, userData);

    if (validation) {
      addBotMessage(`${validation}\n\n${currentQuestion.question}`);
      return;
    }

    // Process the valid input
    let processedValue: any = input;

    if (currentQuestion.type === 'number') {
      processedValue = parseFloat(input);
    } else if (currentQuestion.type === 'boolean') {
      const choice = input.toLowerCase();
      processedValue = choice.includes('1') || choice.includes('yes') || choice.includes('sharia');
    } else if (currentQuestion.type === 'choice') {
      if (currentQuestion.key === 'risk_tolerance') {
        const choice = input.toLowerCase();
        if (choice.includes('1') || choice.includes('conservative')) processedValue = 'conservative';
        else if (choice.includes('2') || choice.includes('moderate')) processedValue = 'moderate';
        else if (choice.includes('3') || choice.includes('aggressive')) processedValue = 'aggressive';
      } else if (currentQuestion.key === 'preferred_market') {
        const choice = input.toLowerCase();
        if (choice.includes('1') || choice.includes('uae')) processedValue = 'UAE';
        else if (choice.includes('2') || choice.includes('us')) processedValue = 'US';
        else if (choice.includes('3') || choice.includes('both')) processedValue = 'Both';
      } else if (currentQuestion.key === 'currency') {
        const choice = input.toLowerCase();
        if (choice.includes('1') || choice.includes('usd')) processedValue = 'USD';
        else if (choice.includes('2') || choice.includes('aed')) processedValue = 'AED';
      }
    } else if (currentQuestion.key === 'goals') {
      // Parse goals from text
      const goalKeywords = ['retirement', 'house', 'education', 'emergency', 'travel', 'business'];
      const detectedGoals = goalKeywords.filter(goal => 
        input.toLowerCase().includes(goal)
      );
      processedValue = detectedGoals.length > 0 ? detectedGoals : ['general_investment'];
    }

    // Update user data
    const newUserData = { ...userData, [currentQuestion.key]: processedValue };
    setUserData(newUserData);

    // Move to next question or complete
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setTimeout(() => {
        addBotMessage(questions[currentQuestionIndex + 1].question);
      }, 1000);
    } else {
      // All questions completed
      setIsCompleted(true);
      setTimeout(() => {
        addBotMessage(
          "Perfect! I have all the information I need to create your personalized financial plan. Here's a summary of what you've told me:\n\n" +
          `• Age: ${newUserData.age}\n` +
          `• Retirement Age: ${newUserData.retirement_age}\n` +
          `• Annual Salary: ${formatCurrency(newUserData.annual_salary || 0, newUserData.currency || 'USD')}\n` +
          `• Annual Expenses: ${formatCurrency(newUserData.annual_expenses || 0, newUserData.currency || 'USD')}\n` +
          `• Current Savings: ${formatCurrency(newUserData.current_savings || 0, newUserData.currency || 'USD')}\n` +
          `• Risk Tolerance: ${newUserData.risk_tolerance}\n` +
          `• Goals: ${Array.isArray(newUserData.goals) ? newUserData.goals.join(', ') : newUserData.goals}\n` +
          `• Sharia Compliant: ${newUserData.is_sharia_compliant ? 'Yes' : 'No'}\n` +
          `• Preferred Market: ${newUserData.preferred_market}\n` +
          `• Currency: ${newUserData.currency}\n\n` +
          "Click 'Generate Financial Plan' to create your personalized investment strategy!"
        );
      }, 1000);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (currentInput.trim() === '') return;

    addUserMessage(currentInput);
    processUserInput(currentInput);
    setCurrentInput('');
  };

  const formatCurrency = (amount: number, currency: string = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg h-96 flex flex-col">
      {/* Chat Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg">
        <h3 className="text-lg font-semibold flex items-center">
          <Bot className="h-5 w-5 mr-2" />
          AI Financial Planner Chat
        </h3>
        <p className="text-blue-100 text-sm">
          Question {Math.min(currentQuestionIndex + 1, questions.length)} of {questions.length}
        </p>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="flex items-start space-x-2">
                {message.type === 'bot' && <Bot className="h-4 w-4 mt-1 flex-shrink-0" />}
                {message.type === 'user' && <User className="h-4 w-4 mt-1 flex-shrink-0" />}
                <p className="text-sm whitespace-pre-line">{message.content}</p>
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      {!isCompleted ? (
        <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              placeholder="Type your answer..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
            <button
              type="submit"
              disabled={currentInput.trim() === ''}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        </form>
      ) : (
        <div className="p-4 border-t border-gray-200 space-y-2">
          <button
            onClick={() => onComplete(userData)}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center justify-center"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Generate Financial Plan
          </button>
          <button
            onClick={onCancel}
            className="w-full px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
          >
            Start Over
          </button>
        </div>
      )}
    </div>
  );
};

export default ChatBasedInput;
