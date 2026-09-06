import math
from sqlalchemy.orm import Session

from app.schemas.sos import SOSCreate
from app.schemas.emergency_response import EmergencyResponseCreate
from app.schemas.notification import NotificationCreate
from app.schemas.hospital_emergency_assignment import (
    HospitalEmergencyAssignmentCreate
)

from app.services.sos_service import SOSService
from app.services.emergency_response_service import (
    EmergencyResponseService
)
from app.services.emergency_contact_service import (
    EmergencyContactService
)
from app.services.notification_service import (
    NotificationService
)
from app.services.hospital_emergency_assignment_service import (
    HospitalEmergencyAssignmentService
)

from app.ai.service import AIIntegrationService
from app.repositories.hospital_repository import HospitalRepository


def calculate_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return float('inf')
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class EmergencyOrchestrationService:

    @staticmethod
    def trigger_emergency(
        db: Session,
        user_id: int,
        sos_data: SOSCreate
    ):

        try:

            # Step 1: Create SOS without committing
            sos = SOSService.create_sos(
                db,
                user_id,
                sos_data,
                commit=False
            )

            # Step 2: Create Emergency Response
            response_data = EmergencyResponseCreate(
                sos_id=sos.sos_id
            )

            response = EmergencyResponseService.create_response(
                db,
                user_id,
                response_data,
                commit=False
            )

            # Step 3: Run AI analysis to determine required medical capability
            patient_context = AIIntegrationService.build_patient_context(
                db,
                user_id
            )

            ai_analysis = AIIntegrationService.analyze_patient_context(
                patient_context=patient_context,
                emergency_description=sos_data.description
            )

            required_capability = ai_analysis.get("required_medical_capability")

            # Step 4: Find active hospitals matching capability & emergency availability
            candidate_hospitals = HospitalRepository.find_matching_hospitals(
                db,
                required_capability
            )

            # Fallback: if no specific capability match found, get all active emergency-available hospitals
            if not candidate_hospitals:
                candidate_hospitals = HospitalRepository.get_active_emergency_hospitals(
                    db
                )

            # Rank candidate hospitals by proximity if SOS lat/lon available
            if sos.latitude is not None and sos.longitude is not None and candidate_hospitals:
                candidate_hospitals.sort(
                    key=lambda h: calculate_distance(
                        sos.latitude,
                        sos.longitude,
                        h.latitude,
                        h.longitude
                    )
                )

            # Step 5: Assign best matching hospital (if any available)
            hospital_assignment = None
            if candidate_hospitals:
                selected_hospital = candidate_hospitals[0]

                assignment_create_data = HospitalEmergencyAssignmentCreate(
                    response_id=response.response_id,
                    hospital_id=selected_hospital.hospital_id
                )

                hospital_assignment = (
                    HospitalEmergencyAssignmentService.create_assignment(
                        db,
                        assignment_create_data,
                        commit=False
                    )
                )

            # Step 6: Get Emergency Contacts and create notifications
            contacts = EmergencyContactService.get_contacts(
                db,
                user_id
            )

            notifications = []

            for contact in contacts:

                notification_data = NotificationCreate(
                    recipient_type="EMERGENCY_CONTACT",
                    recipient_id=contact.contact_id,
                    channel="SMS",
                    message=(
                        "Emergency alert from LifeLink. "
                        "The user has triggered a Master SOS."
                    )
                )

                notification = NotificationService.create_notification(
                    db,
                    user_id,
                    response.response_id,
                    notification_data,
                    commit=False
                )

                notifications.append(notification)

            # Step 7: Commit everything together atomically
            db.commit()

            return {
                "sos": sos,
                "emergency_response": response,
                "emergency_contacts": contacts,
                "notifications": notifications,
                "hospital_assignment": hospital_assignment,
                "required_capability": required_capability
            }

        except Exception:
            db.rollback()
            raise