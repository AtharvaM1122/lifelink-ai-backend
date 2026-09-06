from typing import List

from fastapi import (
    APIRouter,
    Depends,
    status
)
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.hospital_capability import (
    HospitalCapabilityCreate,
    HospitalCapabilityUpdate,
    HospitalCapabilityResponse
)

from app.services.hospital_capability_service import (
    HospitalCapabilityService
)

from app.models.hospital import Hospital
from app.security.dependencies import get_current_hospital


router = APIRouter(
    prefix="/hospitals",
    tags=["Hospital Capabilities"]
)


# ==========================
# Create Hospital Capability
# ==========================

@router.post(
    "/me/capabilities",
    response_model=HospitalCapabilityResponse,
    status_code=status.HTTP_201_CREATED
)
def create_my_capability(
    capability_data: HospitalCapabilityCreate,
    db: Session = Depends(get_db),
    current_hospital: Hospital = Depends(get_current_hospital)
):
    return HospitalCapabilityService.create_capability(
        db,
        current_hospital.hospital_id,
        capability_data
    )


# ==========================
# Bulk Create Hospital Capabilities
# ==========================

@router.post(
    "/me/capabilities/bulk",
    response_model=List[HospitalCapabilityResponse],
    status_code=status.HTTP_201_CREATED
)
def bulk_create_my_capabilities(
    capabilities_data: List[HospitalCapabilityCreate],
    db: Session = Depends(get_db),
    current_hospital: Hospital = Depends(get_current_hospital)
):
    return HospitalCapabilityService.bulk_create_capabilities(
        db,
        current_hospital.hospital_id,
        capabilities_data
    )


# ==========================
# Get My Hospital Capabilities
# ==========================

@router.get(
    "/me/capabilities",
    response_model=List[HospitalCapabilityResponse]
)
def get_my_capabilities(
    db: Session = Depends(get_db),
    current_hospital: Hospital = Depends(get_current_hospital)
):
    return HospitalCapabilityService.get_my_capabilities(
        db,
        current_hospital.hospital_id
    )


# ==========================
# Update Hospital Capability
# ==========================

@router.put(
    "/me/capabilities/{capability_id}",
    response_model=HospitalCapabilityResponse
)
def update_my_capability(
    capability_id: int,
    capability_data: HospitalCapabilityUpdate,
    db: Session = Depends(get_db),
    current_hospital: Hospital = Depends(get_current_hospital)
):
    return HospitalCapabilityService.update_capability(
        db,
        current_hospital.hospital_id,
        capability_id,
        capability_data
    )


# ==========================
# Delete Hospital Capability
# ==========================

@router.delete(
    "/me/capabilities/{capability_id}"
)
def delete_my_capability(
    capability_id: int,
    db: Session = Depends(get_db),
    current_hospital: Hospital = Depends(get_current_hospital)
):
    return HospitalCapabilityService.delete_capability(
        db,
        current_hospital.hospital_id,
        capability_id
    )


# ==========================
# Get Hospital Capabilities By ID
# ==========================

@router.get(
    "/{hospital_id}/capabilities",
    response_model=List[HospitalCapabilityResponse]
)
def get_hospital_capabilities(
    hospital_id: int,
    db: Session = Depends(get_db)
):
    return HospitalCapabilityService.get_capabilities_for_hospital(
        db,
        hospital_id
    )
