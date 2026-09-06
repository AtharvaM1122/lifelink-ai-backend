from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.hospital_capability import HospitalCapability


class HospitalCapabilityRepository:

    @staticmethod
    def create(
        db: Session,
        capability: HospitalCapability
    ) -> HospitalCapability:
        db.add(capability)
        db.commit()
        db.refresh(capability)

        return capability

    @staticmethod
    def bulk_create(
        db: Session,
        capabilities: List[HospitalCapability]
    ) -> List[HospitalCapability]:
        db.add_all(capabilities)
        db.commit()
        for capability in capabilities:
            db.refresh(capability)

        return capabilities

    @staticmethod
    def get_by_id(
        db: Session,
        capability_id: int
    ) -> Optional[HospitalCapability]:
        return (
            db.query(HospitalCapability)
            .filter(
                HospitalCapability.capability_id == capability_id
            )
            .first()
        )

    @staticmethod
    def get_by_hospital_id(
        db: Session,
        hospital_id: int
    ) -> List[HospitalCapability]:
        return (
            db.query(HospitalCapability)
            .filter(
                HospitalCapability.hospital_id == hospital_id
            )
            .all()
        )

    @staticmethod
    def get_by_hospital_and_service(
        db: Session,
        hospital_id: int,
        service_name: str
    ) -> Optional[HospitalCapability]:
        return (
            db.query(HospitalCapability)
            .filter(
                HospitalCapability.hospital_id == hospital_id,
                HospitalCapability.service_name == service_name
            )
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        capability: HospitalCapability
    ) -> HospitalCapability:
        db.commit()
        db.refresh(capability)

        return capability

    @staticmethod
    def delete(
        db: Session,
        capability: HospitalCapability
    ) -> bool:
        db.delete(capability)
        db.commit()

        return True
