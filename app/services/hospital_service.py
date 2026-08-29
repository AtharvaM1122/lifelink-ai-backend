from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.hospital import Hospital

from app.repositories.hospital_repository import (
    HospitalRepository
)

from app.schemas.hospital import (
    HospitalCreate,
    HospitalUpdate
)

from app.security.password import (
    hash_password,
    verify_password
)

from app.security.jwt import create_access_token


class HospitalService:

    @staticmethod
    def register_hospital(
        db: Session,
        hospital_data: HospitalCreate
    ):

        # Check if email already exists
        existing_hospital = (
            HospitalRepository.get_by_email(
                db,
                hospital_data.email
            )
        )

        if existing_hospital:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital with this email already exists."
            )

        # Hash password
        hashed_password = hash_password(
            hospital_data.password
        )

        # Create hospital object
        new_hospital = Hospital(
            hospital_name=hospital_data.hospital_name,
            email=hospital_data.email,
            phone_number=hospital_data.phone_number,
            password_hash=hashed_password,
            address=hospital_data.address,
            latitude=hospital_data.latitude,
            longitude=hospital_data.longitude
        )

        return HospitalRepository.create(
            db,
            new_hospital
        )


    @staticmethod
    def login_hospital(
        db: Session,
        email: str,
        password: str
    ):

        hospital = HospitalRepository.get_by_email(
            db,
            email
        )

        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Verify password
        if not verify_password(
            password,
            hospital.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        # Check hospital status
        if hospital.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hospital account is not active."
            )

        # Generate JWT token
        access_token = create_access_token(
            data={
                "hospital_id": hospital.hospital_id,
                "role": "HOSPITAL"
            }
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


    @staticmethod
    def get_hospital(
        db: Session,
        hospital_id: int
    ):

        hospital = HospitalRepository.get_by_id(
            db,
            hospital_id
        )

        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found."
            )

        return hospital


    @staticmethod
    def get_all_hospitals(
        db: Session
    ):

        return HospitalRepository.get_all(
            db
        )


    @staticmethod
    def update_hospital(
        db: Session,
        hospital_id: int,
        hospital_data: HospitalUpdate
    ):

        hospital = HospitalRepository.get_by_id(
            db,
            hospital_id
        )

        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found."
            )

        update_data = hospital_data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                hospital,
                field,
                value
            )

        return HospitalRepository.update(
            db,
            hospital
        )