from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.hospital_capability import HospitalCapability

from app.repositories.hospital_repository import HospitalRepository
from app.repositories.hospital_capability_repository import (
    HospitalCapabilityRepository
)

from app.schemas.hospital_capability import (
    HospitalCapabilityCreate,
    HospitalCapabilityUpdate
)


class HospitalCapabilityService:

    @staticmethod
    def create_capability(
        db: Session,
        hospital_id: int,
        capability_data: HospitalCapabilityCreate
    ):
        # Check for existing capability with same service_name for this hospital
        existing_capability = (
            HospitalCapabilityRepository.get_by_hospital_and_service(
                db,
                hospital_id,
                capability_data.service_name
            )
        )

        if existing_capability:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Capability with this service name already exists for this hospital."
            )

        new_capability = HospitalCapability(
            hospital_id=hospital_id,
            service_name=capability_data.service_name,
            category=capability_data.category,
            is_available=capability_data.is_available,
            description=capability_data.description
        )

        return HospitalCapabilityRepository.create(
            db,
            new_capability
        )

    @staticmethod
    def bulk_create_capabilities(
        db: Session,
        hospital_id: int,
        capabilities_data: List[HospitalCapabilityCreate]
    ):
        if not capabilities_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Capabilities list cannot be empty."
            )

        existing_caps = HospitalCapabilityRepository.get_by_hospital_id(
            db,
            hospital_id
        )
        existing_names = {c.service_name.lower() for c in existing_caps}

        new_capabilities = []
        seen_in_batch = set()

        for item in capabilities_data:
            name_lower = item.service_name.lower()
            if name_lower in existing_names:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Capability '{item.service_name}' already exists for this hospital."
                )
            if name_lower in seen_in_batch:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate capability '{item.service_name}' in request batch."
                )
            seen_in_batch.add(name_lower)
            new_capabilities.append(
                HospitalCapability(
                    hospital_id=hospital_id,
                    service_name=item.service_name,
                    category=item.category,
                    is_available=item.is_available,
                    description=item.description
                )
            )

        return HospitalCapabilityRepository.bulk_create(
            db,
            new_capabilities
        )

    @staticmethod
    def get_my_capabilities(
        db: Session,
        hospital_id: int
    ):
        return HospitalCapabilityRepository.get_by_hospital_id(
            db,
            hospital_id
        )

    @staticmethod
    def get_capabilities_for_hospital(
        db: Session,
        hospital_id: int
    ):
        # Verify hospital exists
        hospital = HospitalRepository.get_by_id(
            db,
            hospital_id
        )

        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found."
            )

        return HospitalCapabilityRepository.get_by_hospital_id(
            db,
            hospital_id
        )

    @staticmethod
    def update_capability(
        db: Session,
        hospital_id: int,
        capability_id: int,
        capability_data: HospitalCapabilityUpdate
    ):
        capability = HospitalCapabilityRepository.get_by_id(
            db,
            capability_id
        )

        if not capability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Capability record not found."
            )

        # Check ownership
        if capability.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this capability record."
            )

        update_data = capability_data.model_dump(
            exclude_unset=True
        )

        # If service_name is updated, check for duplicates
        if "service_name" in update_data and update_data["service_name"] != capability.service_name:
            existing = HospitalCapabilityRepository.get_by_hospital_and_service(
                db,
                hospital_id,
                update_data["service_name"]
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Capability with this service name already exists for this hospital."
                )

        for field, value in update_data.items():
            setattr(capability, field, value)

        return HospitalCapabilityRepository.update(
            db,
            capability
        )

    @staticmethod
    def delete_capability(
        db: Session,
        hospital_id: int,
        capability_id: int
    ):
        capability = HospitalCapabilityRepository.get_by_id(
            db,
            capability_id
        )

        if not capability:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Capability record not found."
            )

        # Check ownership
        if capability.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to delete this capability record."
            )

        HospitalCapabilityRepository.delete(
            db,
            capability
        )

        return {"message": "Capability deleted successfully."}
