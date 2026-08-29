from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.session import get_db

from app.models.hospital import Hospital

from app.schemas.hospital_emergency_assignment import (
    HospitalEmergencyAssignmentCreate,
    HospitalEmergencyAssignmentUpdate,
    HospitalEmergencyAssignmentResponse
)

from app.services.hospital_emergency_assignment_service import (
    HospitalEmergencyAssignmentService
)

from app.security.dependencies import get_current_hospital


router = APIRouter(
    prefix="/hospital-emergency-assignments",
    tags=["Hospital Emergency Assignments"]
)


# ==========================
# Get My Hospital Assignments
# ==========================

@router.get(
    "/my",
    response_model=List[
        HospitalEmergencyAssignmentResponse
    ]
)
def get_my_assignments(
    db: Session = Depends(get_db),
    current_hospital: Hospital = Depends(
        get_current_hospital
    )
):

    return (
        HospitalEmergencyAssignmentService
        .get_hospital_assignments(
            db,
            current_hospital.hospital_id
        )
    )


# ==========================
# Get Assignment By ID
# ==========================

@router.get(
    "/{assignment_id}",
    response_model=HospitalEmergencyAssignmentResponse
)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_hospital: Hospital = Depends(
        get_current_hospital
    )
):

    assignment = (
        HospitalEmergencyAssignmentService.get_assignment(
            db,
            assignment_id
        )
    )

    if assignment.hospital_id != current_hospital.hospital_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this assignment."
        )

    return assignment

# ==========================
# Update Assignment Status
# ==========================

@router.put(
    "/{assignment_id}",
    response_model=HospitalEmergencyAssignmentResponse
)
def update_assignment(
    assignment_id: int,
    assignment_data: HospitalEmergencyAssignmentUpdate,
    db: Session = Depends(get_db),
    current_hospital: Hospital = Depends(
        get_current_hospital
    )
):

    return (
        HospitalEmergencyAssignmentService
        .update_assignment_status(
            db,
            current_hospital,
            assignment_id,
            assignment_data
        )
    )