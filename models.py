from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    jobs = db.relationship('Job', backref='user', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.String(500))
    ctc = db.Column(db.String(50))
    location = db.Column(db.String(100))
    status = db.Column(db.String(50), default='Applied')
    notes = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)