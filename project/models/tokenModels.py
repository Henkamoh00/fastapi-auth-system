from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    DateTime,
    Boolean,
)
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from project.core import Base
from sqlalchemy.sql import func


class Token(Base):
    __tablename__ = "tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="tokens")

    def __repr__(self):
        return f"<Token(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"
