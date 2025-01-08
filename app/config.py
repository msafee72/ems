import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "9b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ems")