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

    @staticmethod
    def analyze_patient_context(
        patient_context: dict,
        emergency_description: str | None = None
    ) -> dict:
        """
        Generates structured AI health analysis from patient context.
        Supports external LLM inference if GEMINI_API_KEY / OPENAI_API_KEY is configured,
        with robust deterministic fallback synthesis when API keys are absent.
        """
        import os
        import json
        import logging

        logger = logging.getLogger(__name__)

        wallet = patient_context.get("emergency_wallet") or {}
        medical_records = patient_context.get("medical_records") or []
        active_emergency = patient_context.get("emergency") or {}

        # Combine emergency descriptions
        active_desc = emergency_description or active_emergency.get("description")

        # 1. Check for Gemini API key and attempt live LLM inference
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if gemini_api_key:
            try:
                import urllib.request
                prompt = (
                    "You are LifeLink AI, a specialized emergency medical AI assistant. "
                    "Analyze the following patient context and return JSON with exact keys: "
                    "'emergency_understanding', 'severity', 'required_medical_capability', "
                    "'ai_health_summary', 'emergency_report'.\n\n"
                    f"Patient Context: {json.dumps(patient_context, indent=2)}\n"
                    f"Reported Emergency Description: {active_desc or 'None'}\n\n"
                    "Respond with ONLY valid JSON."
                )
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"response_mime_type": "application/json"}
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_body = json.loads(response.read().decode("utf-8"))
                    text = res_body["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(text)

                    logger.info("Gemini AI analysis completed successfully.")

                    return {
                        "emergency_understanding": parsed.get("emergency_understanding"),
                        "severity": parsed.get("severity"),
                        "required_medical_capability": parsed.get("required_medical_capability"),
                        "ai_health_summary": parsed.get("ai_health_summary"),
                        "emergency_report": parsed.get("emergency_report")
                    }
            except Exception as exc:
                logger.warning(f"External Gemini API call failed or timed out: {exc}. Falling back to context synthesis.")

        # 2. Context-aware structured analysis synthesis (Fallback / No API key)
        # Baseline Health Summary
        summary_parts = []
        if wallet.get("blood_group"):
            summary_parts.append(f"Blood Group: {wallet['blood_group']}")
        if wallet.get("allergies"):
            summary_parts.append(f"Allergies: {wallet['allergies']}")
        if wallet.get("chronic_conditions"):
            summary_parts.append(f"Chronic Conditions: {wallet['chronic_conditions']}")
        if wallet.get("current_medications"):
            summary_parts.append(f"Current Medications: {wallet['current_medications']}")

        if medical_records:
            record_titles = [r.get("title") for r in medical_records if r.get("title")]
            if record_titles:
                summary_parts.append(f"Medical History ({len(medical_records)} records): {', '.join(record_titles[:3])}")
        else:
            summary_parts.append("No medical records uploaded.")

        ai_health_summary = "; ".join(summary_parts) if summary_parts else "No emergency wallet data or medical records available."

        # Emergency Understanding & Severity
        combined_text = (
            f"{active_desc or ''} {wallet.get('chronic_conditions') or ''} "
            f"{wallet.get('emergency_notes') or ''} {wallet.get('allergies') or ''}"
        ).lower()

        if active_desc or active_emergency:
            emergency_understanding = f"Active emergency reported: '{active_desc or 'SOS distress signal triggered'}'."
            if any(k in combined_text for k in ["chest pain", "cardiac", "heart", "stroke", "unconscious", "breathing"]):
                severity = "CRITICAL"
                required_capability = "Cardiology Unit, ICU, Emergency Trauma Care"
            elif any(k in combined_text for k in ["fracture", "accident", "bleeding", "severe", "anaphylaxis"]):
                severity = "HIGH"
                required_capability = "Emergency Trauma Care & Orthopedics"
            else:
                severity = "MODERATE"
                required_capability = "General Emergency & Internal Medicine"
        else:
            emergency_understanding = "No active SOS reported. Patient health profile evaluated for emergency readiness."
            severity = "LOW"
            required_capability = "General Outpatient / Internal Medicine"

        # Emergency Report Generation
        report_lines = [
            "==================================================",
            "             LIFELINK EMERGENCY REPORT            ",
            "==================================================",
            f"User ID: {patient_context.get('user_id')}",
            f"Emergency Status: {active_emergency.get('status') if active_emergency else 'No Active SOS'}",
            f"Reported Symptoms/Situation: {active_desc or 'None'}",
            "--------------------------------------------------",
            "PATIENT VITAL PROFILE:",
            f"  - Blood Group: {wallet.get('blood_group') or 'Unknown'}",
            f"  - Known Allergies: {wallet.get('allergies') or 'None listed'}",
            f"  - Chronic Conditions: {wallet.get('chronic_conditions') or 'None listed'}",
            f"  - Active Medications: {wallet.get('current_medications') or 'None listed'}",
            f"  - Emergency Notes: {wallet.get('emergency_notes') or 'None'}",
            "--------------------------------------------------",
            f"ASSESSMENT & CAPABILITIES:",
            f"  - Severity Level: {severity}",
            f"  - Required Hospital Capabilities: {required_capability}",
            "=================================================="
        ]
        emergency_report = "\n".join(report_lines)

        return {
            "emergency_understanding": emergency_understanding,
            "severity": severity,
            "required_medical_capability": required_capability,
            "ai_health_summary": ai_health_summary,
            "emergency_report": emergency_report
        }
