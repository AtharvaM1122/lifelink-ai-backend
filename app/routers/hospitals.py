from typing import List

from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.database.session import get_db

from app.schemas.hospital import (
    HospitalCreate,
    HospitalLogin,
    HospitalUpdate,
    HospitalResponse,
    HospitalToken
)

from app.services.hospital_service import (
    HospitalService
)
from app.models.hospital import Hospital
from app.security.dependencies import get_current_hospital


router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"]
)


# ==========================
# Register Hospital
# ==========================

@router.post(
    "/register",
    response_model=HospitalResponse,
    status_code=status.HTTP_201_CREATED
)
def register_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db)
):

    return HospitalService.register_hospital(
        db,
        hospital_data
    )


# ==========================
# Hospital Login
# ==========================

@router.post(
    "/login",
    response_model=HospitalToken
)
def login_hospital(
    hospital_data: HospitalLogin,
    db: Session = Depends(get_db)
):

    return HospitalService.login_hospital(
        db,
        hospital_data.email,
        hospital_data.password
    )


# ==========================
# Get All Hospitals
# ==========================

@router.get(
    "/",
    response_model=List[HospitalResponse]
)
def get_all_hospitals(
    db: Session = Depends(get_db)
):

    return HospitalService.get_all_hospitals(
        db
    )

# ==========================
# My Hospital Profile
# ==========================
@router.get(
    "/me",
    response_model=HospitalResponse
)
def get_my_hospital(
    current_hospital: Hospital = Depends(
        get_current_hospital
    )
):

    return current_hospital


# ==========================
# Update Hospital
# ==========================

@router.put(
    "/me",
    response_model=HospitalResponse
)
def update_my_hospital(
    hospital_data: HospitalUpdate,
    db: Session = Depends(get_db),
    current_hospital: Hospital = Depends(
        get_current_hospital
    )
):

    return HospitalService.update_hospital(
        db,
        current_hospital.hospital_id,
        hospital_data
    )


# ==========================
# Get Hospital By ID
# ==========================

@router.get(
    "/{hospital_id}",
    response_model=HospitalResponse
)
def get_hospital(
    hospital_id: int,
    db: Session = Depends(get_db)
):

    return HospitalService.get_hospital(
        db,
        hospital_id
    )
