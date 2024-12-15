import os

class Config:
    SECRET_KEY = 'your_secret_key'  # ใช้สำหรับจัดการ Session
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
