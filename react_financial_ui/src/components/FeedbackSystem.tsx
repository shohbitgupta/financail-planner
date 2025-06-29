import React, { useState } from 'react';
import { Star, Send, TrendingUp, Brain, MessageSquare } from 'lucide-react';

interface FeedbackData {
  rating: number;
  feedback_text: string;
  feedback_categories: string[];
  query: string;
  response: string;
  user_profile: any;
  session_id?: string;
  user_id?: string;
}

interface FeedbackSystemProps {
  query: string;
  response: string;
  userProfile: any;
  sessionId?: string;
  userId?: string;
  onFeedbackSubmitted?: (success: boolean) => void;
}

interface LearningInsights {
  system_performance: {
    total_interactions: number;
    average_rating: number;
    improvement_trend: string;
    user_satisfaction_rate: number;
  };
  learning_effectiveness: {
    patterns_identified: number;
    successful_adaptations: number;
    areas_for_improvement: string[];
  };
  recent_analysis: any;
}

const FeedbackSystem: React.FC<FeedbackSystemProps> = ({
  query,
  response,
  userProfile,
  sessionId,
  userId,
  onFeedbackSubmitted
}) => {
  const [rating, setRating] = useState<number>(0);
  const [feedbackText, setFeedbackText] = useState<string>('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [showInsights, setShowInsights] = useState<boolean>(false);
  const [insights, setInsights] = useState<LearningInsights | null>(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<boolean>(false);

  const feedbackCategories = [
    { id: 'accuracy', label: 'Accuracy', description: 'Information correctness' },
    { id: 'relevance', label: 'Relevance', description: 'How relevant to your needs' },
    { id: 'clarity', label: 'Clarity', description: 'Easy to understand' },
    { id: 'completeness', label: 'Completeness', description: 'Covers all important aspects' }
  ];

  const handleStarClick = (starRating: number) => {
    setRating(starRating);
  };

  const handleCategoryToggle = (categoryId: string) => {
    setSelectedCategories(prev => 
      prev.includes(categoryId) 
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const submitFeedback = async () => {
    if (rating === 0) {
      alert('Please provide a rating');
      return;
    }

    setIsSubmitting(true);

    const feedbackData: FeedbackData = {
      rating,
      feedback_text: feedbackText,
      feedback_categories: selectedCategories,
      query,
      response,
      user_profile: userProfile,
      session_id: sessionId,
      user_id: userId
    };

    try {
      const apiUrl = process.env.NODE_ENV === 'production' 
        ? process.env.REACT_APP_API_URL || 'https://your-api-domain.com'
        : 'http://localhost:5001';

      const response = await fetch(`${apiUrl}/api/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedbackData),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Feedback submitted successfully:', result);
        setFeedbackSubmitted(true);
        onFeedbackSubmitted?.(true);
        
        // Reset form
        setRating(0);
        setFeedbackText('');
        setSelectedCategories([]);
      } else {
        const error = await response.json();
        console.error('Failed to submit feedback:', error);
        alert('Failed to submit feedback. Please try again.');
        onFeedbackSubmitted?.(false);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Error submitting feedback. Please try again.');
      onFeedbackSubmitted?.(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const fetchLearningInsights = async () => {
    try {
      const apiUrl = process.env.NODE_ENV === 'production' 
        ? process.env.REACT_APP_API_URL || 'https://your-api-domain.com'
        : 'http://localhost:5001';

      const response = await fetch(`${apiUrl}/api/learning-insights`);
      
      if (response.ok) {
        const insightsData = await response.json();
        setInsights(insightsData);
        setShowInsights(true);
      } else {
        console.error('Failed to fetch learning insights');
        alert('Failed to fetch learning insights');
      }
    } catch (error) {
      console.error('Error fetching learning insights:', error);
      alert('Error fetching learning insights');
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'declining':
        return <TrendingUp className="w-4 h-4 text-red-500 transform rotate-180" />;
      default:
        return <TrendingUp className="w-4 h-4 text-gray-500" />;
    }
  };

  if (feedbackSubmitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 mt-6">
        <div className="flex items-center space-x-2 text-green-700">
          <Brain className="w-5 h-5" />
          <h3 className="font-semibold">Thank you for your feedback!</h3>
        </div>
        <p className="text-green-600 mt-2">
          Your feedback helps improve our AI financial planner through reinforcement learning.
        </p>
        <button
          onClick={fetchLearningInsights}
          className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
        >
          <Brain className="w-4 h-4" />
          <span>View Learning Insights</span>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 mt-6">
      <div className="flex items-center space-x-2 mb-4">
        <MessageSquare className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-800">Help Improve Our AI</h3>
        <Brain className="w-5 h-5 text-purple-600" />
      </div>
      
      <p className="text-gray-600 mb-4">
        Your feedback trains our reinforcement learning system to provide better financial advice.
      </p>

      {/* Rating */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          How would you rate this financial plan?
        </label>
        <div className="flex space-x-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              onClick={() => handleStarClick(star)}
              className={`p-1 rounded transition-colors ${
                star <= rating ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'
              }`}
            >
              <Star className="w-6 h-6 fill-current" />
            </button>
          ))}
        </div>
        {rating > 0 && (
          <p className="text-sm text-gray-600 mt-1">
            {rating === 1 && "Poor - Needs significant improvement"}
            {rating === 2 && "Fair - Some improvements needed"}
            {rating === 3 && "Good - Meets basic expectations"}
            {rating === 4 && "Very Good - Exceeds expectations"}
            {rating === 5 && "Excellent - Outstanding quality"}
          </p>
        )}
      </div>

      {/* Feedback Categories */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What aspects would you like to comment on? (Optional)
        </label>
        <div className="grid grid-cols-2 gap-2">
          {feedbackCategories.map((category) => (
            <button
              key={category.id}
              onClick={() => handleCategoryToggle(category.id)}
              className={`p-3 rounded-lg border text-left transition-colors ${
                selectedCategories.includes(category.id)
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="font-medium text-sm">{category.label}</div>
              <div className="text-xs text-gray-500">{category.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Feedback Text */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional Comments (Optional)
        </label>
        <textarea
          value={feedbackText}
          onChange={(e) => setFeedbackText(e.target.value)}
          placeholder="Share specific feedback to help us improve..."
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
        />
      </div>

      {/* Submit Button */}
      <div className="flex justify-between items-center">
        <button
          onClick={fetchLearningInsights}
          className="px-4 py-2 text-blue-600 hover:text-blue-700 transition-colors flex items-center space-x-2"
        >
          <Brain className="w-4 h-4" />
          <span>View Learning Insights</span>
        </button>
        
        <button
          onClick={submitFeedback}
          disabled={isSubmitting || rating === 0}
          className={`px-6 py-2 rounded-lg transition-colors flex items-center space-x-2 ${
            isSubmitting || rating === 0
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          <Send className="w-4 h-4" />
          <span>{isSubmitting ? 'Submitting...' : 'Submit Feedback'}</span>
        </button>
      </div>

      {/* Learning Insights Modal */}
      {showInsights && insights && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold flex items-center space-x-2">
                <Brain className="w-5 h-5 text-purple-600" />
                <span>AI Learning Insights</span>
              </h3>
              <button
                onClick={() => setShowInsights(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              {/* System Performance */}
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-800 mb-2">System Performance</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Total Interactions:</span>
                    <span className="ml-2 font-medium">{insights.system_performance.total_interactions}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Average Rating:</span>
                    <span className="ml-2 font-medium">{insights.system_performance.average_rating.toFixed(1)}/5</span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-gray-600">Trend:</span>
                    <span className="ml-2 flex items-center space-x-1">
                      {getTrendIcon(insights.system_performance.improvement_trend)}
                      <span className="font-medium capitalize">{insights.system_performance.improvement_trend}</span>
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Satisfaction Rate:</span>
                    <span className="ml-2 font-medium">{(insights.system_performance.user_satisfaction_rate * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>

              {/* Learning Effectiveness */}
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-medium text-green-800 mb-2">Learning Effectiveness</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Patterns Identified:</span>
                    <span className="ml-2 font-medium">{insights.learning_effectiveness.patterns_identified}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Successful Adaptations:</span>
                    <span className="ml-2 font-medium">{insights.learning_effectiveness.successful_adaptations}</span>
                  </div>
                </div>
                
                {insights.learning_effectiveness.areas_for_improvement.length > 0 && (
                  <div className="mt-3">
                    <span className="text-gray-600 text-sm">Areas for Improvement:</span>
                    <ul className="mt-1 text-sm">
                      {insights.learning_effectiveness.areas_for_improvement.map((area, index) => (
                        <li key={index} className="text-gray-700">• {area}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackSystem;
