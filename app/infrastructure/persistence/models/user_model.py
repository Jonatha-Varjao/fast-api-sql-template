import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from sqlalchemy_utils import Timestamp
from app.infrastructure.persistence.base import Base


class UserModel(Base, Timestamp):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), index=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(), nullable=True)
    email = Column(String(255), index=True, unique=True)
    document = Column(String(14), unique=True, nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


class EnvironmentModel(Base, Timestamp):
    __tablename__ = 'environments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=True)


class PermissionModel(Base, Timestamp):
    __tablename__ = 'permissions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    code_name = Column(String(255), unique=True, nullable=True)
    description = Column(String(255), nullable=True)


class GroupModel(Base, Timestamp):
    __tablename__ = 'groups'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    environment_id = Column(UUID(as_uuid=True), ForeignKey('environments.id'), nullable=True)


# Association tables
class EnvUser(Base, Timestamp):
    __tablename__ = 'env_user'
    user_id = Column(UUID(), ForeignKey('users.id'), primary_key=True)
    environment_id = Column(UUID(), ForeignKey('environments.id'), primary_key=True)
    is_admin = Column(Boolean(), nullable=True)
    extra_data = Column(String(50), nullable=True)


class UserPermission(Base, Timestamp):
    __tablename__ = 'user_permission'
    permission_id = Column(UUID(), ForeignKey('permissions.id'), primary_key=True)
    user_id = Column(UUID(), ForeignKey('users.id'), primary_key=True)
    extra_data = Column(String(50), nullable=True)


class GroupPermission(Base, Timestamp):
    __tablename__ = 'group_permission'
    group_id = Column(UUID(), ForeignKey('groups.id'), primary_key=True)
    permission_id = Column(UUID(), ForeignKey('permissions.id'), primary_key=True)
    extra_data_json = Column(JSON, nullable=True)


class UserGroup(Base, Timestamp):
    __tablename__ = 'user_group'
    group_id = Column(UUID(), ForeignKey('groups.id'), primary_key=True)
    user_id = Column(UUID(), ForeignKey('users.id'), primary_key=True)
    extra_data = Column(String(50), nullable=True)
