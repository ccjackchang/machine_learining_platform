from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Framework_version(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    framework = db.Column(db.String(100))
    version = db.Column(db.String(100), unique=True)

class Gpu_status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.String(100), unique=True)
    gpu_name = db.Column(db.String(100))

class task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    docker_name = db.Column(db.String(1000), unique=True)
    gpu = db.Column(db.String(100))
    start_time = db.Column(db.String(100))