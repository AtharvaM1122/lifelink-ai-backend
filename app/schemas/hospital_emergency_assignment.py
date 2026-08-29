from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ==========================
# Create Assignment
# ==========================

class HospitalEmergencyAssignmentCreate(BaseModel):

    response_id: int
    hospital_id: int


# ==========================
# Update Assignment Status
# ==========================

class HospitalEmergencyAssignmentUpdate(BaseModel):

    status: str


# ==========================
# Assignment Response
# ==========================

class HospitalEmergencyAssignmentResponse(BaseModel):

    assignment_id: int

    response_id: int
    hospital_id: int

    status: str

    assigned_at: datetime

    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )