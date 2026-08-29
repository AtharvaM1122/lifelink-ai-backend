from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.hospital import Hospital

from app.repositories.hospital_repository import (
    HospitalRepository
)

from app.repositories.emergency_response_repository import (
    EmergencyResponseRepository
)

from app.repositories.hospital_emergency_assignment_repository import (
    HospitalEmergencyAssignmentRepository
)

from app.models.hospital_emergency_assignment import (
    HospitalEmergencyAssignment
)

from app.schemas.hospital_emergency_assignment import (
    HospitalEmergencyAssignmentCreate,
    HospitalEmergencyAssignmentUpdate
)

from app.repositories.sos_repository import (
    SOSRepository
)


class HospitalEmergencyAssignmentService:

    @staticmethod
    def create_assignment(
        db: Session,
        assignment_data: HospitalEmergencyAssignmentCreate
    ):

        # Check if emergency response exists
        response = (
            EmergencyResponseRepository.get_by_id(
                db,
                assignment_data.response_id
            )
        )

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency response not found."
            )

        # Check if hospital exists
        hospital = HospitalRepository.get_by_id(
            db,
            assignment_data.hospital_id
        )

        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found."
            )

        # Check if hospital is active
        if hospital.status != "ACTIVE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital is not active."
            )

        # Check if hospital is available for emergencies
        if not hospital.emergency_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital is currently unavailable for emergencies."
            )

        # Check if response is already assigned
        existing_assignment = (
            HospitalEmergencyAssignmentRepository.get_by_response(
                db,
                assignment_data.response_id
            )
        )

        if existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Emergency response is already assigned to a hospital."
            )

        # Create assignment
        new_assignment = HospitalEmergencyAssignment(
            response_id=assignment_data.response_id,
            hospital_id=assignment_data.hospital_id,
            status="ASSIGNED"
        )

        return (
            HospitalEmergencyAssignmentRepository.create(
                db,
                new_assignment
            )
        )


    @staticmethod
    def get_assignment(
        db: Session,
        assignment_id: int
    ):

        assignment = (
            HospitalEmergencyAssignmentRepository.get_by_id(
                db,
                assignment_id
            )
        )

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency assignment not found."
            )

        return assignment


    @staticmethod
    def get_hospital_assignments(
        db: Session,
        hospital_id: int
    ):

        return (
            HospitalEmergencyAssignmentRepository.get_by_hospital(
                db,
                hospital_id
            )
        )


    @staticmethod
    def update_assignment_status(
        db: Session,
        hospital: Hospital,
        assignment_id: int,
        assignment_data: HospitalEmergencyAssignmentUpdate
    ):

        assignment = (
            HospitalEmergencyAssignmentRepository.get_by_id(
                db,
                assignment_id
            )
        )

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Emergency assignment not found."
            )

        # Ensure assignment belongs to current hospital
        if assignment.hospital_id != hospital.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this assignment."
            )

        allowed_transitions = {
            "ASSIGNED": ["ACCEPTED"],
            "ACCEPTED": ["IN_PROGRESS"],
            "IN_PROGRESS": ["COMPLETED"],
            "COMPLETED": []
        }

        current_status = assignment.status
        new_status = assignment_data.status

        if new_status not in allowed_transitions.get(
            current_status,
            []
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid status transition: "
                    f"{current_status} -> {new_status}."
                )
            )

        # Update status
        assignment.status = new_status

        # Record acceptance time
        if new_status == "ACCEPTED":

            assignment.accepted_at = datetime.now(
                timezone.utc
            )

        # Complete the entire emergency lifecycle
        if new_status == "COMPLETED":

            assignment.completed_at = datetime.now(
                timezone.utc
            )

            # Get linked emergency response
            response = (
                EmergencyResponseRepository.get_by_id(
                    db,
                    assignment.response_id
                )
            )

            if response:

                # Complete emergency response
                response.status = "COMPLETED"

                # Get linked SOS
                sos = SOSRepository.get_by_id(
                    db,
                    response.sos_id
                )

                if sos and sos.status == "ACTIVE":

                    sos.status = "RESOLVED"

                    sos.resolved_at = datetime.now(
                        timezone.utc
                    )

        try:

            db.commit()
            db.refresh(assignment)

            return assignment

        except Exception:

            db.rollback()
            raise

        