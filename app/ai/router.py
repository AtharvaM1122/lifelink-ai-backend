from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.security.dependencies import get_current_user

from app.ai.schemas import (
    AIHealthAnalysisRequest,
    AIHealthAnalysisResponse
)

from app.ai.service import AIIntegrationService
from app.ai.readiness_service import ReadinessService


router = APIRouter(
    prefix="/ai",
    tags=["AI Integration"]
)


@router.get(
    "/readiness/{user_id}"
)
def get_readiness_score(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this readiness score."
        )

    score = ReadinessService.calculate_readiness_score(
        db,
        user_id
    )

    return {
        "user_id": user_id,
        "readiness_score": score
    }


@router.post(
    "/analysis",
    response_model=AIHealthAnalysisResponse
)
def analyze_health(
    request: AIHealthAnalysisRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.user_id != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this analysis."
        )

    patient_context = AIIntegrationService.build_patient_context(
        db,
        request.user_id
    )

    readiness_score = ReadinessService.calculate_readiness_score(
        db,
        request.user_id
    )

    analysis_result = AIIntegrationService.analyze_patient_context(
        patient_context=patient_context,
        emergency_description=request.emergency_description
    )

    return {
        "user_id": request.user_id,
        "readiness_score": readiness_score,
        "ai_health_summary": analysis_result.get("ai_health_summary"),
        "emergency_understanding": analysis_result.get("emergency_understanding"),
        "severity": analysis_result.get("severity"),
        "required_medical_capability": analysis_result.get("required_medical_capability"),
        "emergency_report": analysis_result.get("emergency_report")
    }