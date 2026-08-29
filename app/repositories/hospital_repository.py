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