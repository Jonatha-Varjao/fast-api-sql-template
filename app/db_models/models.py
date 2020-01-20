from uuid import uuid4

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Unicode, Boolean
from sqlalchemy_utils import Timestamp

from app.db.base import Base


class User(Base, Timestamp):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name = Column(String(255), index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), index=True, unique=True)
    password = Column(String)
    is_superuser = Column(Boolean, unique=False, default=False)
    is_active = Column(Boolean, unique=False, default=True)
