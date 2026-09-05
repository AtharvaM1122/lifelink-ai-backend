from typing import Optional, List
from pydantic import BaseModel, Field


# =========================================================
# Medical Record Information
# =========================================================

class AIMedicalRecord(BaseModel):

    record_id: int
    record_type: str
    title: str

    hospital_name: Optional[str] = None
    doctor_name: Optional[str] = None
    record_date: Optional[str] = None

    ocr_text: Optional[str] = None


# =========================================================
# Emergency Wallet Information
# =========================================================

class AIEmergencyWallet(BaseModel):

    blood_group: Optional[str] = None

    allergies: Optional[str] = None

    chronic_conditions: Optional[str] = None

    current_medications: Optional[str] = None

    emergency_notes: Optional[str] = None


# =========================================================
# Emergency Information
# =========================================================

class AIEmergency(BaseModel):

    sos_id: Optional[int] = None

    description: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    status: Optional[str] = None


# =========================================================
# AI Analysis Request
# =========================================================

class AIHealthAnalysisRequest(BaseModel):

    user_id: int

    emergency_description: Optional[str] = None

    emergency_wallet: Optional[AIEmergencyWallet] = None

    medical_records: List[AIMedicalRecord] = Field(default_factory=list)

    emergency: Optional[AIEmergency] = None


# =========================================================
# AI Analysis Response
# =========================================================

class AIHealthAnalysisResponse(BaseModel):

    user_id: int

    readiness_score: Optional[int] = None

    emergency_understanding: Optional[str] = None

    severity: Optional[str] = None

    required_medical_capability: Optional[str] = None

    ai_health_summary: Optional[str] = None

    emergency_report: Optional[str] = None