"""
    TODO:
        - CRUD GROUP
        - STRESS TEST - 1000, 10.000, 100.000, 1.000.000
"""
from fastapi.encoders import jsonable_encoder

from app import crud
from app.db.session import db_session
from app.models.user import UserCreate
from app.tests.utils.utils import random_lower_string


def test_create_group():
    pass

def test_get_group():
    pass

def test_update_group():
    pass

def test_delete_group():
    pass