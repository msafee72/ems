import sys
import os
import pytest
import logging
from werkzeug.security import generate_password_hash

# Add the project directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, mongo

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "MONGO_URI": "mongodb://localhost:27017/ems_test"  # Ensure this is a test database
    })

    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def init_database():
    # Ensure we are using a test database
    db_name = mongo.db.name
    if db_name != "ems_test":
        raise RuntimeError(f"Attempting to run tests on non-test database: {db_name}")

 # Setup: Create test users, candidates, and elections
    logging.debug("Setting up the test database")
    mongo.db.users.insert_one({"username": "zohaib@12345", "password": generate_password_hash("12345", method="sha256")})
    mongo.db.users.insert_one({"username": "khokhar123", "password": generate_password_hash("123", method="sha256")})
    mongo.db.candidates2.insert_one({"name": "John Doe", "party": "Democratic Party", "age": 45})
    mongo.db.elections.insert_one({"electionName": "Presidential Election", "startDate": "2024-01-01", "endDate": "2024-01-31", "description": "Description of the election"})
    mongo.db.voters.insert_one({ "name": "Voter One", "age": 30,"voterID": "V12345"})
    mongo.db.voters.insert_one({ "name": "Voter Two", "age": 25,"voterID": "V12346"})
    mongo.db.votes.insert_many([
        {"voter_id": "V12345", "candidate_id": "67693faa95c3e628cfa2f901", "candidate_name": "John Doe", "candidate_party": "Democratic Party"},
        {"voter_id": "V12346", "candidate_id": "67693faa95c3e628cfa2f902", "candidate_name": "Jane Smith", "candidate_party": "Republican Party"}
    ])

    
    yield

    # Teardown: Drop the test database
    logging.debug("Tearing down the test database")
    mongo.db.users.drop()
    mongo.db.candidates2.drop()
    mongo.db.elections.drop()
    mongo.db.votes2.drop()
    mongo.db.voters.drop()