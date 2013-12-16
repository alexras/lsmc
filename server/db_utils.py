import os, db_utils

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from flask import g

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = db_utils.connect()
    return db

def close_db(db):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def connect():

    return session
