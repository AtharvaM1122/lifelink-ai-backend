from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    TIMESTAMP
)
from sqlalchemy.sql import func

from app.database.base import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    hospital_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    hospital_name = Column(
        String(150),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=False
    )

    phone_number = Column(
        String(15),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    address = Column(
        String(255),
        nullable=False
    )

    latitude = Column(
        Float,
        nullable=True
    )

    longitude = Column(
        Float,
        nullable=True
    )

    emergency_available = Column(
        Boolean,
        nullable=False,
        default=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )