from sqlalchemy.orm import Session

from app.models.hospital import Hospital


class HospitalRepository:

    @staticmethod
    def create(
        db: Session,
        hospital: Hospital
    ):
        db.add(hospital)
        db.commit()
        db.refresh(hospital)

        return hospital

    @staticmethod
    def get_by_id(
        db: Session,
        hospital_id: int
    ):
        return (
            db.query(Hospital)
            .filter(
                Hospital.hospital_id == hospital_id
            )
            .first()
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str
    ):
        return (
            db.query(Hospital)
            .filter(
                Hospital.email == email
            )
            .first()
        )

    @staticmethod
    def get_all(
        db: Session
    ):
        return (
            db.query(Hospital)
            .all()
        )

    @staticmethod
    def find_matching_hospitals(
        db: Session,
        required_capability: str = None
    ):
        import re
        from app.models.hospital_capability import HospitalCapability
        from sqlalchemy import or_

        query = (
            db.query(Hospital)
            .filter(
                Hospital.status == "ACTIVE",
                Hospital.emergency_available == True
            )
        )

        STOP_WORDS = {
            "unit", "care", "general", "department", "hospital", "emergency",
            "transport", "dispatch", "immediate", "personnel", "with", "facility",
            "services", "system", "response", "medical", "level", "type", "status",
            "required", "capabilities", "needs", "patient", "trained", "support",
            "life", "advanced", "rapid", "acls"
        }

        if required_capability:
            raw_parts = re.split(r'[,&/]| \band\b ', required_capability, flags=re.IGNORECASE)
            terms = set()
            for part in raw_parts:
                cleaned = part.strip()
                if cleaned and cleaned.lower() not in STOP_WORDS:
                    # Check individual words
                    words = [w for w in cleaned.split() if len(w) > 2 and w.lower() not in STOP_WORDS]
                    if words:
                        for w in words:
                            terms.add(w)

            if terms:
                ilike_conditions = [
                    HospitalCapability.service_name.ilike(f"%{term}%")
                    for term in terms
                ]
                query = query.join(
                    HospitalCapability,
                    Hospital.hospital_id == HospitalCapability.hospital_id
                ).filter(
                    HospitalCapability.is_available == True,
                    or_(*ilike_conditions)
                )

        return query.distinct().all()

    @staticmethod
    def get_active_emergency_hospitals(
        db: Session
    ):
        return (
            db.query(Hospital)
            .filter(
                Hospital.status == "ACTIVE",
                Hospital.emergency_available == True
            )
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        hospital: Hospital
    ):
        db.commit()
        db.refresh(hospital)

        return hospital

    @staticmethod
    def delete(
        db: Session,
        hospital: Hospital
    ):
        db.delete(hospital)
        db.commit()

        return True