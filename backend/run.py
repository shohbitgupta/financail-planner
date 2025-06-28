"""
Entry point for the Financial Planner AI backend application.
"""
import os
from app import create_app

# Get configuration from environment
config_name = os.environ.get('FLASK_CONFIG', 'development')

# Create Flask application
app = create_app(config_name)

if __name__ == '__main__':
    # Development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001)),
        debug=app.config.get('DEBUG', False)
    )
