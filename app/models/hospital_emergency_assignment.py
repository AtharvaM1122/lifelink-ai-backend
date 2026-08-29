from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)

from sqlalchemy.sql import func

from app.database.base import Base


class HospitalEmergencyAssignment(Base):

    __tablename__ = "hospital_emergency_assignments"


    assignment_id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    # Emergency being assigned
    response_id = Column(
        Integer,
        ForeignKey(
            "emergency_responses.response_id"
        ),
        nullable=False,
        index=True
    )


    # Hospital receiving the emergency
    hospital_id = Column(
        Integer,
        ForeignKey(
            "hospitals.hospital_id"
        ),
        nullable=False,
        index=True
    )


    # Current assignment status
    status = Column(
        String(20),
        nullable=False,
        default="ASSIGNED"
    )


    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


    accepted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )


    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )