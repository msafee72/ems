from flask_login import UserMixin
from app import mongo, login_manager
from bson import ObjectId

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = str(user_id)  # Ensure the user_id is a string
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_id=user_data["_id"], username=user_data["username"])
    return None