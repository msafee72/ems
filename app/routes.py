from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import mongo
from datetime import datetime
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

# Create a Blueprint for the main routes
main = Blueprint("main", __name__)

# Home route
@main.route("/")
def home():
    return render_template("home.html")  # Rendering the base template


@main.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("main.register"))

        # Check if the username already exists
        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user:
            flash("Username already exists. Please choose a different username.", "danger")
            return redirect(url_for("main.register"))

        hashed_password = generate_password_hash(password, method="sha256")
        mongo.db.users.insert_one({"username": username, "password": hashed_password})
        return render_template("message.html", message="User registered successfully!")  # Render a message template

    return render_template("register.html")

@main.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user_data = mongo.db.users.find_one({"username": username})
        if user_data and check_password_hash(user_data["password"], password):
            user = User(user_id=user_data["_id"], username=user_data["username"])
            login_user(user)
            return render_template("message.html", message="Logged in successfully!")  # Render a message template
        else:
            return render_template("error.html", message="Invalid username or password"), 401

    return render_template("login.html")
# Route to logout a user
@main.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("message.html", message="logged out successfully!")  # Render a message template




# Route to add a candidate (admin only)
@main.route("/add_candidate", methods=["POST", "GET"])
@login_required
def add_candidate():
    if current_user.username != "zohaib@12345":  # Replace with your specific admin username
        return render_template("error.html", message="You do not have permission to access this page."), 403

    if request.method == "POST":
        data = request.form
        if not data.get("name") or not data.get("party"):
            return render_template("error.html", message="Missing candidate name or party"), 400

        # Check for duplicate candidate
        if mongo.db.candidates2.find_one({"name": data.get("name"), "party": data.get("party")}):
            return render_template("error.html", message="Candidate already exists!"), 400

        # Insert candidate into the candidates collection
        mongo.db.candidates2.insert_one({
            "name": data.get("name"),
            "party": data.get("party")
        })
        return render_template("message.html", message="Candidate added successfully!")  # Render a message template

    return render_template("add_candidate.html")





# Route to register a voter (admin only)
@main.route("/register_voter", methods=["POST", "GET"])
@login_required
def register_voter():
    if current_user.username != "zohaib@12345":  # Replace with your specific admin username
        return render_template("error.html", message="You do not have permission to access this page."), 403

    if request.method == "POST":
        data = request.form
        if not data.get("name") or not data.get("age") or not data.get("voterID"):
            return render_template("error.html", message="Missing voter name, age, or voter ID"), 400

        # Check for duplicate voter ID
        if mongo.db.voters.find_one({"voterID": data.get("voterID")}):
            return render_template("error.html", message="Voter ID already exists!"), 400

        # Check age restriction
        if int(data.get("age")) < 18:
            return render_template("error.html", message="Voter is not eligible due to age restriction"), 400

        # Insert voter into the voters collection
        mongo.db.voters.insert_one({
            "name": data.get("name"),
            "age": data.get("age"),
            "voterID": data.get("voterID")
        })
        return render_template("message.html", message="Voter registered successfully!")  # Render a message template

    return render_template("add_voter.html")




# Route to add an election (admin only)
@main.route("/add_election", methods=["POST", "GET"])
@login_required
def add_election():
    if current_user.username != "zohaib@12345":  # Replace with your specific admin username
        return render_template("error.html", message="You do not have permission to access this page."), 403

    if request.method == "POST":
        data = request.form
        election_data = {
            "electionName": data.get("electionName"),
            "startDate": data.get("startDate"),
            "endDate": data.get("endDate"),
            "description": data.get("description"),
        }

        if not election_data["electionName"] or not election_data["startDate"] or not election_data["endDate"]:
            return render_template("error.html", message="Missing election name, start date, or end date"), 400

        # Check for scheduling conflicts
        conflicting_election = mongo.db.elections.find_one({
            "$or": [
                {"startDate": {"$lte": election_data["endDate"], "$gte": election_data["startDate"]}},
                {"endDate": {"$lte": election_data["endDate"], "$gte": election_data["startDate"]}},
                {"startDate": {"$lte": election_data["startDate"]}, "endDate": {"$gte": election_data["endDate"]}}
            ]
        })

        if conflicting_election:
            return render_template("error.html", message="Scheduling conflict with another election"), 400

        # Insert election into the elections collection
        mongo.db.elections.insert_one(election_data)
        return render_template("message.html", message="Election added successfully!")  # Render a message template

    return render_template("add_election.html")





# Route to view all candidates2
@main.route("/view_candidates", methods=["GET"])
@login_required
def view_candidates():
    if current_user.username != "zohaib@12345":  # Replace with your specific admin username
        return render_template("error.html", message="You do not have permission to access this page."), 403
    candidates = list(mongo.db.candidates2.find({}, {"_id": 0}))
    return render_template("view_candidates.html", candidates=candidates)

# Route to view all voters
@main.route("/view_voters", methods=["GET"])
@login_required
def view_voters():
    voters = list(mongo.db.voters.find({}, {"_id": 0}))  # Exclude _id in response
    return render_template("view_voters.html", voters=voters)  # Render view voters template with data

# Route to view all elections
@main.route("/view_elections", methods=["GET"])
@login_required
def view_elections():
    elections = list(mongo.db.elections.find({}, {"_id": 0}))  # Exclude _id in response
    return render_template("view_elections.html", elections=elections)  # Render view elections template with data



# Route to cast a vote
@main.route("/cast_vote", methods=["POST", "GET"])
@login_required
def cast_vote():
    if request.method == "POST":
        # Get data from the form (instead of JSON in this case, since it's a form submission)
        voter_id = request.form.get("voter_id")
        candidate_id = request.form.get("candidate_id")
        candidate_name = request.form.get("candidate_name")
        candidate_party = request.form.get("candidate_party")

        if not voter_id or not candidate_id or not candidate_name or not candidate_party:
            return render_template("error.html", message="Missing voter ID, candidate ID, candidate name, or candidate party"), 400

        # Check if voter exists
        voter = mongo.db.voters.find_one({"voterID": voter_id})
        if not voter:
            return render_template("error.html", message="Voter not found"), 404

        # Check if the voter has already voted
        existing_vote = mongo.db.votes2.find_one({"voterID": voter_id})
        if existing_vote:
            return render_template("error.html", message="Voter has already cast a vote"), 400

        # Insert vote into the votes collection
        mongo.db.votes2.insert_one({
            "voterID": voter_id,
            "candidateID": candidate_id,
            "timestamp": datetime.utcnow(),
            "candidateName": candidate_name,
            "Party": candidate_party
        })
        return render_template("message.html", message="Vote cast successfully!")

    # If the request is GET, fetch candidates and render the form
    candidates = mongo.db.candidates2.find()  # Get all candidates from the database
    return render_template("cast_vote.html", candidates=candidates)  # Pass candidates to the template



# Route to view all votes
@main.route("/view_votes", methods=["GET"])
@login_required
def view_votes():
    votes = list(mongo.db.votes2.find({}, {"_id": 0}))  # Exclude _id in response
    return render_template("view_votes.html", votes=votes)  # Render view votes template with data