from datetime import datetime,timezone
from sqlalchemy import Date
from sqlalchemy import (
    Column,
    String,
    DateTime,
    Boolean,
)
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from project.core import Base


# User Model
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firstName = Column(String(255), nullable=False)
    lastName = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False, unique=True)
    gender = Column(Boolean, nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    emailIsVerified = Column(Boolean, nullable=False, default=False)
    phoneNumber = Column(String(20))
    locations = Column(String(255))
    birthDate = birthDate = Column(Date)
    birthPlace = Column(String(255))
    hashed_password = Column(String(255), nullable=False)  # Assuming hashed password
    profilePhoto = Column(String(255))
    registrationDate = Column(DateTime(timezone=True), nullable=False, default=func.now())
    isActive = Column(Boolean, nullable=False, default=True)
    last_password_change = Column(DateTime(timezone=True), nullable=False, default=datetime.now(timezone.utc))

    # Relationships
    tokens = relationship("Token", back_populates="user", lazy="selectin", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"