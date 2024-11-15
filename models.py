import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    public_key = db.Column(db.String, nullable=False)
    private_key = db.Column(db.String, nullable=False)

class EncryptedEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_deleted = db.Column(db.Boolean, default=False)
    receiver_deleted = db.Column(db.Boolean, default=False)
    sender_deleted = db.Column(db.Boolean, default=False)
    trash_date = db.Column(db.DateTime)
    is_read = db.Column(db.Boolean, default=False)

class EncryptForward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_body = db.Column(db.Integer, db.ForeignKey('encrypted_email.id'), nullable=False)
    key_sender = db.Column(db.Text, nullable=False)
    key_receiver = db.Column(db.Text, nullable=False)

