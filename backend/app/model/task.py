import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum,Text
import enum
from app.core.database import Base

class TaskStatus(str,enum.Enum):
    PENDING = "pending"
    STARTED = "started"
    COMPLETED = "completed"

class Task(Base):
    __tablename__ = "tasks"
    id=Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title=Column(String(255), nullable=False)
    description=Column(Text, nullable=True)
    status=Column(Enum(TaskStatus),nullable=False, default=TaskStatus.PENDING)
    org_id=Column(String,nullable=False,index=True)
    created_by=Column(String,nullable=False)
    created_at=Column(DateTime, default=datetime.utcnow)
    updated_at=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)