from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


# ==========================
# Create Hospital Capability
# ==========================

class HospitalCapabilityCreate(BaseModel):

    service_name: str
    category: Optional[str] = None
    is_available: bool = True
    description: Optional[str] = None


# ==========================
# Bulk Create Hospital Capabilities
# ==========================

class HospitalCapabilityBulkCreate(BaseModel):

    capabilities: List[HospitalCapabilityCreate]


# ==========================
# Update Hospital Capability
# ==========================

class HospitalCapabilityUpdate(BaseModel):

    service_name: Optional[str] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None
    description: Optional[str] = None


# ==========================
# Hospital Capability Response
# ==========================

class HospitalCapabilityResponse(BaseModel):

    capability_id: int
    hospital_id: int
    service_name: str
    category: Optional[str] = None
    is_available: bool
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
