import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_DIR"] = os.path.abspath(
    os.path.join(SCRIPT_DIR, os.pardir, "uploads"))

db = SQLAlchemy(app)

import server.orm

db.create_all()

import server.views
