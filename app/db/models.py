import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .engine import Base
from typing import List
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    first_name: Mapped[str] = mapped_column(nullable=False)

    last_name: Mapped[str] = mapped_column(nullable=True)

    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)

    phone_number: Mapped[str] = mapped_column(nullable=False, unique=True)

    is_verified: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    teams: Mapped[List["TeamUser"]] = relationship("TeamUser", back_populates="user")

    tasks: Mapped[List["UserTask"]] = relationship(
        "UserTask",
        back_populates="user",
        foreign_keys="UserTask.user_id",
    )

    assigned_tasks: Mapped[List["UserTask"]] = relationship(
        "UserTask", foreign_keys="UserTask.assigned_by_id", back_populates="assigned_by"
    )

    password_hash: Mapped[str] = mapped_column(sa.String(255), nullable=False)


class TeamModel(Base):
    __tablename__ = "teams"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(
        nullable=False,
    )
    description: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    owner_id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    owner: Mapped["UserModel"] = relationship("UserModel", foreign_keys=[owner_id])

    users: Mapped[List["TeamUser"]] = relationship("TeamUser", back_populates="team")


class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    name: Mapped[str] = mapped_column(
        nullable=False,
    )

    description: Mapped[str] = mapped_column(nullable=True)

    goal: Mapped[str] = mapped_column(nullable=True)

    ttl: Mapped[int] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    title: Mapped[str] = mapped_column(
        nullable=False,
    )

    description: Mapped[str] = mapped_column(nullable=True)

    status: Mapped[str] = mapped_column(nullable=False)

    priority: Mapped[str] = mapped_column(nullable=False, default="medium")

    __table_args__ = (
        sa.CheckConstraint(
            "status IN ('done', 'in_progress', 'todo')", name="check_task_status"
        ),
        sa.CheckConstraint(
            "priority IN ('high', 'medium', 'low')", name="check_task_priority"
        ),
    )

    due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa.func.now(),
        server_onupdate=sa.func.now(),
        nullable=False,
    )

    users: Mapped[List["UserTask"]] = relationship("UserTask", back_populates="task")


class TeamUser(Base):
    __tablename__ = "team_user"

    user_id: Mapped[UUID] = mapped_column(sa.ForeignKey("users.id"), primary_key=True)
    team_id: Mapped[UUID] = mapped_column(sa.ForeignKey("teams.id"), primary_key=True)

    role_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("roles.id"),
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=sa.func.now(), nullable=False
    )

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="teams")

    team: Mapped["TeamModel"] = relationship("TeamModel", back_populates="users")

    role: Mapped["RoleModel"] = relationship("RoleModel")


class UserTask(Base):
    __tablename__ = "user_task"

    user_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id"),
        primary_key=True,
    )

    task_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("tasks.id"),
        primary_key=True,
    )

    assigned_by_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey("users.id"),
        nullable=True,
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa.func.now(),
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="tasks",
        foreign_keys=[user_id],
    )

    assigned_by: Mapped["UserModel"] = relationship(
        "UserModel",
        foreign_keys=[assigned_by_id],
        back_populates="assigned_tasks",
    )

    task: Mapped["TaskModel"] = relationship(
        "TaskModel",
        back_populates="users",
    )


class RoleModel(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    name: Mapped[str] = mapped_column(
        nullable=False,
    )

    description: Mapped[str] = mapped_column(nullable=True)


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(sa.ForeignKey("users.id"), index =True, nullable=False)

    token: Mapped[str] = mapped_column(unique=True, nullable=False)

    expires_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    revoked: Mapped[bool] = mapped_column(sa.Boolean, default=False)


class OTP(Base):
    __tablename__ = "otp"

    id: Mapped[UUID] = mapped_column(
        sa.UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    user_id: Mapped[UUID | None] = mapped_column(
        sa.ForeignKey("users.id"), index=True, nullable=True
    )

    channel: Mapped[str] = mapped_column(
        nullable=False,
    )

    target: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
        index=True,
    )

    purpose: Mapped[str] = mapped_column(
        nullable=False,
        index=True,
    )

    __table_args__ = (
    sa.CheckConstraint(
        "channel IN ('sms', 'email')", name="otp_channel"
    ),
    sa.CheckConstraint(
        "purpose IN ('login', 'verify_email', 'verify_phone', 'reset_password')", name="otp_purpose"
    ),
    sa.Index(
        "ix_otp_target_purpose_channel", "target", "purpose", "channel"
    ),
    )

    code_hash: Mapped[str] = mapped_column(
        sa.String(255),
        nullable=False,
    )

    attempts: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
    )

    is_used: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    last_sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=sa.func.now(),
        nullable=False,
    )
