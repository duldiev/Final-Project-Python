from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = '86fc238c0e1d9af308ef7e9249e09496'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/postgres2'
db = SQLAlchemy(app)

from flaskblog import routes
