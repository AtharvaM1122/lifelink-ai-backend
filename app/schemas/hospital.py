from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


# ==========================
# Create Hospital
# ==========================

class HospitalCreate(BaseModel):

    hospital_name: str
    email: EmailStr
    phone_number: str
    password: str

    address: str

    latitude: Optional[float] = None
    longitude: Optional[float] = None


# ==========================
# Hospital Login
# ==========================

class HospitalLogin(BaseModel):

    email: EmailStr
    password: str


# ==========================
# Update Hospital
# ==========================

class HospitalUpdate(BaseModel):

    hospital_name: Optional[str] = None
    phone_number: Optional[str] = None

    address: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    emergency_available: Optional[bool] = None

    


# ==========================
# Hospital Response
# ==========================

class HospitalResponse(BaseModel):

    hospital_id: int

    hospital_name: str
    email: EmailStr
    phone_number: str

    address: str

    latitude: Optional[float]
    longitude: Optional[float]

    emergency_available: bool
    status: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# ==========================
# Hospital Token
# ==========================

class HospitalToken(BaseModel):

    access_token: str
    token_type: str