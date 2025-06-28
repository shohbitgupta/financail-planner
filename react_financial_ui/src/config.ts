// API Configuration
export const API_CONFIG = {
  // Cloud API URL - Replace with your deployed Render URL
  CLOUD_API_URL: process.env.REACT_APP_API_URL || 'https://financial-planner-ai-api.onrender.com',

  // Local development URL
  LOCAL_API_URL: process.env.REACT_APP_LOCAL_API_URL || 'http://localhost:5001',

  // Determine which URL to use based on environment
  BASE_URL: process.env.NODE_ENV === 'production'
    ? (process.env.REACT_APP_API_URL || 'https://financial-planner-ai-api.onrender.com')
    : (process.env.REACT_APP_LOCAL_API_URL || 'http://localhost:5001'),

  // API endpoints
  ENDPOINTS: {
    HEALTH: '/api/health',
    GENERATE_PLAN: '/api/generate-financial-plan'
  }
};

// Helper function to get full API URL
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

// Export the main API URL for easy access
export const API_BASE_URL = API_CONFIG.BASE_URL;
