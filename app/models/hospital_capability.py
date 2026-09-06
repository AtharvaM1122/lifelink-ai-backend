from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    TIMESTAMP,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class HospitalCapability(Base):
    __tablename__ = "hospital_capabilities"
    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "service_name",
            name="uq_hospital_service"
        ),
    )

    capability_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.hospital_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    service_name = Column(
        String(100),
        nullable=False
    )

    category = Column(
        String(50),
        nullable=True
    )

    is_available = Column(
        Boolean,
        nullable=False,
        default=True
    )

    description = Column(
        String(255),
        nullable=True
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

    hospital = relationship(
        "Hospital",
        back_populates="capabilities"
    )
