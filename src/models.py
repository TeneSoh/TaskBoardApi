from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)
    profile_image = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)
    last_login = Column(DateTime, nullable=True)
    role = Column(String(50), nullable=True)

    project = relationship(
        "Project", back_populates="user", cascade="all, delete-orphan"
    )
    comment = relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )
    task = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE")
    )

    user = relationship("User", back_populates="project")
    task = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    status = Column(
        Enum("todo", "in_progress", "done", name="task_status", create_type=False),
        default="todo",
    )
    priority = Column(
        Enum("low", "medium", "high", name="task_priority", create_type=False),
        default="low",
    )
    deadline = Column(DateTime)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE")
    )

    project = relationship("Project", back_populates="task")
    comment = relationship(
        "Comment", back_populates="task", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="task")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(255), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    task = relationship("Task", back_populates="comment")
    user = relationship("User", back_populates="comment")
