"""
Health check endpoint for Vercel deployment
"""

import json
import os
from datetime import datetime

def handler(request):
    """Health check handler"""
    
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Financial Planner AI Agent',
        'version': '1.0.0',
        'environment': 'production',
        'features': {
            'financial_planning': True,
            'ai_recommendations': True,
            'wio_bank_integration': True,
            'risk_assessment': True
        }
    }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(health_data)
    }

# For Vercel deployment
def main(request):
    return handler(request)
