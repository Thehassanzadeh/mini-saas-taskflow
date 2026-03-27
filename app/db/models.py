import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .engine import Base
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime



class UserModel(Base):
    __tablename__ = "users"

    id:
    first_name:
    last_name:
    email:
    is_verified:
    create_at:

class TeamModel(Base):
    __tablename__ = "teams"

    id:
    name:
    description:
    create_at:


class ProjectModel(Base):
    __tablename__ = "projects"

    id:
    name:
    description:
    goal:
    ttl:
    create_at:


class TaskModel(Base):
    __tablename__ = "tasks"

    id:
    title:
    description:
    status:
    priority:
    assigned_to:
    due_data:
    create_at:
    update_at:


class TeamUser(Base):
    __tablename__ = "task-user"

    id:

class UserTask(Base):
    __tablename__ = "user-task"

class RoleModel(Base):
    __tablename__ = "roles"
    id:
    name:
    description:
    