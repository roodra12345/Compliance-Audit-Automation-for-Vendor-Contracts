import os
from app import create_app

# Get environment from env variable
env = os.environ.get('FLASK_ENV', 'development')

# Create app
app = create_app(env)

if __name__ == '__main__':
    # Run the application
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=(env == 'development')
    )