"""
AI-powered consultation endpoint (Scenario 2).
"""
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.auth import get_current_user
from app.database import get_db
from app.services.gemini_service import get_ai_chat_response, get_ai_consultation

router = APIRouter(prefix="/advisor", tags=["advisor"])


@router.post("/consult", response_model=schemas.AdvisorResponse)
def consult(
    request: schemas.AdvisorRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    profile = current_user.profile
    if profile is None:
        raise HTTPException(status_code=404, detail="No credit profile yet. Submit one via POST /credit/profile first.")

    metrics = {
        "credit_score": profile.credit_score,
        "credit_band": profile.credit_band.value,
        "monthly_income": profile.monthly_income,
        "monthly_expenses": profile.monthly_expenses,
        "total_debt": profile.total_debt,
        "debt_to_income_ratio": profile.debt_to_income_ratio,
        "utilization_ratio": profile.utilization_ratio,
        "missed_payments_last_year": profile.missed_payments_last_year,
    }

    result = get_ai_consultation(metrics, goal=request.goal)

    crud.save_advisor_session(
        db,
        user_id=current_user.id,
        input_snapshot=metrics,
        analysis=result["analysis"],
        action_plan=result["action_plan"],
    )

    return schemas.AdvisorResponse(
        analysis=result["analysis"],
        action_plan=result["action_plan"],
        credit_band=profile.credit_band,
        generated_at=dt.datetime.utcnow(),
    )


@router.post("/chat", response_model=schemas.AdvisorChatResponse)
def chat(
    request: schemas.AdvisorChatRequest,
    current_user: models.User = Depends(get_current_user),
):
    profile = current_user.profile
    if profile is None:
        raise HTTPException(status_code=404, detail="Submit your credit profile before chatting with the advisor.")

    metrics = {
        "credit_score": profile.credit_score,
        "credit_band": profile.credit_band.value,
        "monthly_income": profile.monthly_income,
        "monthly_expenses": profile.monthly_expenses,
        "total_debt": profile.total_debt,
        "debt_to_income_ratio": profile.debt_to_income_ratio,
        "utilization_ratio": profile.utilization_ratio,
        "missed_payments_last_year": profile.missed_payments_last_year,
    }
    messages = [message.model_dump() for message in request.messages]
    return schemas.AdvisorChatResponse(reply=get_ai_chat_response(metrics, messages))
