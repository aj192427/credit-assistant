"""
Credit profile input, and the dashboard data feed (Scenarios 1, 3, 4).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/credit", tags=["credit"])


@router.post("/profile", response_model=schemas.CreditProfileOut)
def submit_profile(
    data: schemas.CreditProfileIn,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Onboarding (Scenario 1) and real-time updates (Scenario 4) share this endpoint:
    it always recalculates DTI/utilization/band and appends a history snapshot,
    so the dashboard reflects the change immediately.
    """
    profile = crud.upsert_credit_profile(db, current_user, data)
    return profile


@router.get("/dashboard", response_model=schemas.DashboardOut)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Single call that feeds the whole dashboard: current snapshot, full score
    history for the line chart (Scenario 3), and deltas vs. the previous
    snapshot for the "improvement" indicators (Scenario 4).
    """
    if current_user.profile is None:
        raise HTTPException(status_code=404, detail="No credit profile yet. Submit one via POST /credit/profile.")

    history = crud.get_score_history(db, current_user.id)

    score_delta = None
    utilization_delta = None
    if len(history) >= 2:
        score_delta = history[-1].credit_score - history[-2].credit_score
        utilization_delta = round(history[-1].utilization_ratio - history[-2].utilization_ratio, 2)

    return schemas.DashboardOut(
        profile=current_user.profile,
        history=history,
        score_delta=score_delta,
        utilization_delta=utilization_delta,
    )
