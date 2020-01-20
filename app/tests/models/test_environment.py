"""
    TODO:
        - CRUD ENVIRONMENT
        - STRESS TEST - 1000, 10.000, 100.000, 1.000.000
        - CRUD USER_ENVIROMENT ASSOCIATION TABLE
"""
from fastapi.encoders import jsonable_encoder

from app import crud
from app.db.session import db_session
from app.models.user import UserCreate
from app.tests.utils.utils import random_lower_string

def test_create_environment():
    pass

def test_get_environment():
    pass

def test_update_environment():
    pass

def test_delete_environment():
    pass