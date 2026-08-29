from sqlalchemy.orm import Session

from app.models.hospital_emergency_assignment import (
    HospitalEmergencyAssignment
)


class HospitalEmergencyAssignmentRepository:

    @staticmethod
    def create(
        db: Session,
        assignment: HospitalEmergencyAssignment
    ):
        db.add(assignment)
        db.commit()
        db.refresh(assignment)

        return assignment


    @staticmethod
    def get_by_id(
        db: Session,
        assignment_id: int
    ):
        return (
            db.query(HospitalEmergencyAssignment)
            .filter(
                HospitalEmergencyAssignment.assignment_id
                == assignment_id
            )
            .first()
        )


    @staticmethod
    def get_by_response(
        db: Session,
        response_id: int
    ):
        return (
            db.query(HospitalEmergencyAssignment)
            .filter(
                HospitalEmergencyAssignment.response_id
                == response_id
            )
            .first()
        )


    @staticmethod
    def get_by_hospital(
        db: Session,
        hospital_id: int
    ):
        return (
            db.query(HospitalEmergencyAssignment)
            .filter(
                HospitalEmergencyAssignment.hospital_id
                == hospital_id
            )
            .all()
        )


    @staticmethod
    def update(
        db: Session,
        assignment: HospitalEmergencyAssignment
    ):
        db.commit()
        db.refresh(assignment)

        return assignment