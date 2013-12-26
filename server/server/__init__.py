import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager

from celery import Celery

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config.update(
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db",
    UPLOAD_DIR = os.path.abspath(
        os.path.join(SCRIPT_DIR, os.pardir, "uploads")),
    CELERY_BROKER_URL='amqp://guest@localhost//'
)

# Set up ORM layer for DB

db = SQLAlchemy(app)

import server.orm

db.create_all()

# Wrap ORM in a REST API

manager = APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(server.orm.SAVFile, methods=["GET", "PUT"])

# Add a task queue for async processing

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(app)

import server.views
import server.async
