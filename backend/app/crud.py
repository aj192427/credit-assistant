"""
Database read/write helpers, kept out of the route handlers for testability.
"""
import json

from sqlalchemy.orm import Session

from app import models, schemas
from app.services.credit_calc import recalculate_profile_fields


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_in: schemas.UserCreate, hashed_password: str) -> models.User:
    user = models.User(
        full_name=user_in.full_name,
        email=user_in.email,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def upsert_credit_profile(
    db: Session, user: models.User, data: schemas.CreditProfileIn
) -> models.CreditProfile:
    """
    Creates or updates the user's current profile snapshot, recalculates derived
    fields (DTI, utilization, band), and appends a row to score history so the
    dashboard's trend line and deltas (Scenario 3 & 4) stay accurate.
    """
    derived = recalculate_profile_fields(
        credit_score=data.credit_score,
        monthly_income=data.monthly_income,
        total_debt=data.total_debt,
        credit_used=data.credit_used,
        total_credit_limit=data.total_credit_limit,
    )

    profile = user.profile
    if profile is None:
        profile = models.CreditProfile(user_id=user.id)
        db.add(profile)

    profile.credit_score = data.credit_score
    profile.monthly_income = data.monthly_income
    profile.monthly_expenses = data.monthly_expenses
    profile.total_debt = data.total_debt
    profile.total_credit_limit = data.total_credit_limit
    profile.credit_used = data.credit_used
    profile.missed_payments_last_year = data.missed_payments_last_year
    profile.debt_to_income_ratio = derived["debt_to_income_ratio"]
    profile.utilization_ratio = derived["utilization_ratio"]
    profile.credit_band = derived["credit_band"]

    # Append a history snapshot every time the profile is updated, so the
    # progress chart (Scenario 3) and the improvement delta (Scenario 4) work.
    history_row = models.CreditScoreHistory(
        user_id=user.id,
        credit_score=data.credit_score,
        utilization_ratio=derived["utilization_ratio"],
        debt_to_income_ratio=derived["debt_to_income_ratio"],
    )
    db.add(history_row)

    db.commit()
    db.refresh(profile)
    return profile


def get_score_history(db: Session, user_id: int, limit: int = 100):
    return (
        db.query(models.CreditScoreHistory)
        .filter(models.CreditScoreHistory.user_id == user_id)
        .order_by(models.CreditScoreHistory.recorded_at.asc())
        .limit(limit)
        .all()
    )


def save_advisor_session(
    db: Session,
    user_id: int,
    input_snapshot: dict,
    analysis: str,
    action_plan: list[str],
) -> models.AdvisorSession:
    session = models.AdvisorSession(
        user_id=user_id,
        input_snapshot=json.dumps(input_snapshot),
        ai_analysis=analysis,
        action_plan=json.dumps(action_plan),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
