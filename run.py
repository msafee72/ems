import logging
from app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO)

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get('DEBUG', True), port=5002)

