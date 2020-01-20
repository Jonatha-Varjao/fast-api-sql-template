from uuid import uuid4

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import String, Unicode, Boolean
from sqlalchemy_utils import Timestamp

from app.db.base import Base


class EnvUser(Base, Timestamp):
    __tablename__ = 'env_user'
    user_id = Column(UUID, ForeignKey('users.id'), primary_key=True)
    environment_id = Column(UUID, ForeignKey('environments.id'), primary_key=True)
    is_admin = Column(Boolean, unique=False, default=False)
    extra_data = Column(String(50))

    user = relationship("User", back_populates="environments")
    environment = relationship("Environment", back_populates="users")


class UserPermission(Base, Timestamp):
    __tablename__ = 'user_permission'
    permission_id = Column(UUID, ForeignKey('permissions.id'), primary_key=True)
    user_id = Column(UUID, ForeignKey('users.id'), primary_key=True)
    extra_data = Column(String(50))

    permission = relationship("Permission", back_populates="users")
    user = relationship("User", back_populates="permissions")


class UserGroup(Base, Timestamp):
    __tablename__ = 'user_group'
    group_id = Column(UUID, ForeignKey('groups.id'), primary_key=True)
    user_id = Column(UUID, ForeignKey('users.id'), primary_key=True)
    extra_data = Column(String(50))

    group = relationship("Group", back_populates="users")
    user = relationship("User", back_populates="groups")


class GroupPermission(Base, Timestamp):
    __tablename__ = 'group_permission'
    group_id = Column(UUID, ForeignKey("groups.id"), primary_key=True)
    permission_id = Column(UUID, ForeignKey("permissions.id"), primary_key=True)
    extra_data_json = Column(JSON(none_as_null=True))

    group = relationship("Group", back_populates="permissions")
    permission = relationship("Permission", back_populates="groups")


class User(Base, Timestamp):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    full_name = Column(String(255), index=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String)
    email = Column(String(255), index=True, unique=True)
    document = Column(Unicode(14), unique=True)
    phone_number = Column(Unicode(20), unique=True)
    is_superuser = Column(Boolean, unique=False, default=False)
    is_active = Column(Boolean, unique=False, default=True)

    environments = relationship('EnvUser', back_populates="user", cascade="all, delete, delete-orphan")
    permissions = relationship('UserPermission', back_populates="user", cascade="all, delete, delete-orphan")
    groups = relationship('UserGroup', back_populates="user", cascade="all, delete, delete-orphan")


class Permission(Base, Timestamp):
    __tablename__ = 'permissions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True, index=True)
    code_name = Column(String(255), unique=True, index=True)
    description = Column(String(255))

    groups = relationship('GroupPermission', back_populates="permission", cascade="all, delete, delete-orphan")
    users = relationship('UserPermission', back_populates="permission", cascade="all, delete, delete-orphan")


class Group(Base, Timestamp):
    __tablename__ = 'groups'
    __table_args__ = (UniqueConstraint('name', 'environment_id', name='uix_name_environment'),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255))
    description = Column(String(255))
    environment_id = Column(UUID(as_uuid=True), ForeignKey('environments.id'))

    users = relationship('UserGroup', back_populates="group", cascade="all, delete, delete-orphan")
    permissions = relationship('GroupPermission', back_populates="group", cascade="all, delete, delete-orphan")
    environment = relationship('Environment', back_populates="group")


class Environment(Base, Timestamp):
    __tablename__ = 'environments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), unique=True)

    users = relationship(EnvUser, back_populates="environment", cascade="all, delete, delete-orphan")
    group = relationship(Group, back_populates="environment", cascade="all, delete, delete-orphan")
