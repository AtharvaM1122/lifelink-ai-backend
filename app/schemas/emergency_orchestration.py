from typing import List, Optional

from app.schemas.sos import SOSResponse
from app.schemas.emergency_response import EmergencyResponseResponse
from app.schemas.emergency_contact import EmergencyContactResponse
from app.schemas.notification import NotificationResponse
from app.schemas.hospital_emergency_assignment import HospitalEmergencyAssignmentResponse

from pydantic import BaseModel


class EmergencyTriggerResponse(BaseModel):
    sos: SOSResponse
    emergency_response: EmergencyResponseResponse
    emergency_contacts: List[EmergencyContactResponse]
    notifications: List[NotificationResponse]
    hospital_assignment: Optional[HospitalEmergencyAssignmentResponse] = None
    required_capability: Optional[str] = None