from sqlalchemy.orm import Session

from app.repositories.emergency_wallet_repository import (
    EmergencyWalletRepository
)

from app.repositories.medical_record_repository import (
    MedicalRecordRepository
)

from app.repositories.sos_repository import (
    SOSRepository
)


class AIIntegrationService:

    @staticmethod
    def build_patient_context(
        db: Session,
        user_id: int
    ):

        wallet = EmergencyWalletRepository.get_by_user(
            db,
            user_id
        )

        medical_records = MedicalRecordRepository.get_by_user(
            db,
            user_id
        )

        active_sos = SOSRepository.get_active_by_user(
            db,
            user_id
        )

        return {
            "user_id": user_id,

            "emergency_wallet": {
                "blood_group": (
                    wallet.blood_group
                    if wallet else None
                ),
                "allergies": (
                    wallet.allergies
                    if wallet else None
                ),
                "chronic_conditions": (
                    wallet.chronic_conditions
                    if wallet else None
                ),
                "current_medications": (
                    wallet.current_medications
                    if wallet else None
                ),
                "emergency_notes": (
                    wallet.emergency_notes
                    if wallet else None
                )
            },

            "medical_records": [
                {
                    "record_id": record.record_id,
                    "record_type": record.record_type,
                    "title": record.title,
                    "hospital_name": record.hospital_name,
                    "doctor_name": record.doctor_name,
                    "record_date": (
                        record.record_date.isoformat()
                        if record.record_date
                        else None
                    ),
                    "ocr_text": record.ocr_text
                }
                for record in medical_records
            ],

            "emergency": (
                {
                    "sos_id": active_sos.sos_id,
                    "description": active_sos.description,
                    "latitude": active_sos.latitude,
                    "longitude": active_sos.longitude,
                    "status": active_sos.status
                }
                if active_sos
                else None
            )
        }