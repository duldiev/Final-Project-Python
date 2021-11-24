from flaskblog import db
from datetime import datetime


class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crypto_name = db.Column(db.String(20), nullable=False)
    header = db.Column(db.Text, nullable=False)
    paragraph = db.Column(db.Text, nullable=False)

    def __init__(self, crypto_name, header, paragraph):
        self.crypto_name = crypto_name
        self.header = header
        self.paragraph = paragraph


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    token = db.Column(db.Text, nullable=False, default='')

    def __init__(self, username, email, password, token):
        self.username = username
        self.email = email
        self.password = password
        self.token = token