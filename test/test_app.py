import pytest
from flask import url_for


# tests/test_app.py
def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to the Election Management System" in response.data


# 1. Voter Registration
def test_register_voter(client, init_database):
    # Log in as admin
    response = client.post('/login', data={
        "username": "zohaib@12345",
        "password": "12345"
    })
    assert response.status_code == 200
    assert b"Logged in successfully!" in response.data

    response = client.post('/register_voter', data={
        "name": "Jane Doe",
        "age": 30,
        "voterID": "V12342"
    })
    assert response.status_code == 200
    assert b"Voter registered successfully!" in response.data

    # Test duplicate ID
    response = client.post('/register_voter', data={
        "name": "Jane Doe",
        "age": 30,
        "voterID": "V12342"
    })
    assert response.status_code == 400
    assert b"Voter ID already exists" in response.data

    # Test missing details
    response = client.post('/register_voter', data={
        "name": "",
        "age": 30,
        "voterID": "V12349"
    })
    assert response.status_code == 400
    assert b"Missing voter name, age, or voter ID" in response.data

    # Test age restriction
    response = client.post('/register_voter', data={
        "name": "Young Voter",
        "age": 15,
        "voterID": "V12378"
    })
    assert response.status_code == 400
    assert b"Voter is not eligible due to age restriction" in response.data



# 2. Candidate Management
def test_add_candidate(client, init_database):
    # Log in as admin
    response = client.post('/login', data={
        "username": "zohaib@12345",
        "password": "12345"
    })
    assert response.status_code == 200
    assert b"Logged in successfully!" in response.data

    response = client.post('/add_candidate', data={
        "name": "Jane Smith",
        "party": "Republican Party"
    })
    assert response.status_code == 200
    assert b"Candidate added successfully!" in response.data

    # Test duplicate candidate
    response = client.post('/add_candidate', data={
        "name": "Jane Smith",
        "party": "Republican Party"
    })
    assert response.status_code == 400
    assert b"Candidate already exists" in response.data


# 3. Election Scheduling
def test_create_election(client, init_database):
    # Log in as admin
    response = client.post('/login', data={
        "username": "zohaib@12345",
        "password": "12345"
    })
    assert response.status_code == 200
    assert b"Logged in successfully!" in response.data

    response = client.post('/add_election', data={
        "electionName": "Senate Election",
        "startDate": "2024-02-01",
        "endDate": "2024-02-28",
        "description": "Description of the election"
    })
    assert response.status_code == 200
    assert b"Election added successfully!" in response.data

    # Test scheduling conflict
    response = client.post('/add_election', data={
        "electionName": "Conflicting Election",
        "startDate": "2024-01-15",
        "endDate": "2024-02-15",
        "description": "Description of the election"
    })
    assert response.status_code == 400
    assert b"Scheduling conflict with another election" in response.data

#vote casting
def test_cast_vote(client, init_database):
    # Log in as voter
    response = client.post('/login', data={
        "username": "khokhar123",
        "password": "123"
    })
    assert response.status_code == 200
    assert b"Logged in successfully!" in response.data

    response = client.post('/cast_vote', data={
        "voter_id": "V12345",
        "candidate_id": "67693faa95c3e628cfa2f901",
        "candidate_name": "John Doe",
        "candidate_party": "Democratic Party"
    })
    assert response.status_code == 200
    assert b"Vote cast successfully!" in response.data

    # Test duplicate vote
    response = client.post('/cast_vote', data={
        "voter_id": "V12345",
        "candidate_id": "67693faa95c3e628cfa2f901",
        "candidate_name": "John Doe",
        "candidate_party": "Democratic Party"
    })
    assert response.status_code == 400
    assert b"Voter has already cast a vote" in response.data



#5. Results and Analytics
def test_view_votes(client, init_database):
    # Log in as admin
    response = client.post('/login', data={ 
        "username": "zohaib@12345",
        "password": "12345"
    })
    assert response.status_code == 200
    assert b"Logged in successfully!" in response.data

    response = client.get('/view_votes')
    assert response.status_code == 200

    # Log the response data for debugging
    response_data = response.data.decode('utf-8')
    print(response_data)

    assert b"All Votes" in response.data


# 6. Role-Based Access
def test_admin_access(client, init_database):
    # Test admin access
    response = client.post('/login', data={
        "username": "zohaib@12345",
        "password": "12345"
    })
    assert response.status_code == 200
    assert b"Logged in successfully!" in response.data

    response = client.get('/add_candidate')
    assert response.status_code == 200

    # Test voter access
    response = client.post('/login', data={
        "username": "khokhar123",
        "password": "123"
    })
    assert response.status_code == 200
    assert b"Logged in successfully!" in response.data

    response = client.get('/add_candidate')
    assert response.status_code == 403
    assert b"You do not have permission to access this page." in response.data


