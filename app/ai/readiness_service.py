from sqlalchemy.orm import Session

from app.repositories.emergency_wallet_repository import (
    EmergencyWalletRepository
)

from app.repositories.medical_record_repository import (
    MedicalRecordRepository
)


class ReadinessService:

    @staticmethod
    def calculate_readiness_score(
        db: Session,
        user_id: int
    ) -> int:

        wallet = EmergencyWalletRepository.get_by_user(
            db,
            user_id
        )

        records = MedicalRecordRepository.get_by_user(
            db,
            user_id
        )

        score = 0

        if wallet:

            wallet_fields = [
                wallet.blood_group,
                wallet.allergies,
                wallet.chronic_conditions,
                wallet.current_medications,
                wallet.emergency_notes
            ]

            completed_fields = sum(
                1
                for field in wallet_fields
                if field is not None and str(field).strip()
            )

            score += completed_fields * 15

        if records:
            score += 25

        return min(score, 100)