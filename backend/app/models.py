"""
Database models.

- User: account/auth
- CreditProfile: the user's current financial snapshot (score, income, debts, utilization)
- CreditScoreHistory: time series of credit score snapshots, for the progress chart
- AdvisorSession: stores each AI consultation (request + Gemini response) for auditability
"""
import datetime as dt
import enum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship

from app.database import Base


class CreditBand(str, enum.Enum):
    POOR = "Poor"          # < 580
    FAIR = "Fair"          # 580-669
    GOOD = "Good"           # 670-739
    VERY_GOOD = "Very Good"  # 740-799
    EXCELLENT = "Excellent"  # 800-900 (CIBIL scale used in India)


def band_for_score(score: int) -> CreditBand:
    if score < 580:
        return CreditBand.POOR
    if score < 670:
        return CreditBand.FAIR
    if score < 740:
        return CreditBand.GOOD
    if score < 800:
        return CreditBand.VERY_GOOD
    return CreditBand.EXCELLENT


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    profile = relationship("CreditProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    score_history = relationship("CreditScoreHistory", back_populates="user", cascade="all, delete-orphan")
    advisor_sessions = relationship("AdvisorSession", back_populates="user", cascade="all, delete-orphan")


class CreditProfile(Base):
    """The user's latest/current financial snapshot."""
    __tablename__ = "credit_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    credit_score = Column(Integer, nullable=False)          # 300-900 (CIBIL-style)
    monthly_income = Column(Float, nullable=False)           # INR
    monthly_expenses = Column(Float, nullable=False)         # INR
    total_debt = Column(Float, nullable=False, default=0)    # outstanding debt, INR
    total_credit_limit = Column(Float, nullable=False, default=0)  # sum of credit card limits, INR
    credit_used = Column(Float, nullable=False, default=0)   # current revolving balance, INR
    missed_payments_last_year = Column(Integer, nullable=False, default=0)

    # Derived/calculated fields, recomputed server-side on every update
    debt_to_income_ratio = Column(Float, nullable=False, default=0)  # %
    utilization_ratio = Column(Float, nullable=False, default=0)     # %
    credit_band = Column(Enum(CreditBand), nullable=False, default=CreditBand.FAIR)

    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    user = relationship("User", back_populates="profile")


class CreditScoreHistory(Base):
    """One row per snapshot in time -> powers the progress line chart."""
    __tablename__ = "credit_score_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    credit_score = Column(Integer, nullable=False)
    utilization_ratio = Column(Float, nullable=False)
    debt_to_income_ratio = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=dt.datetime.utcnow)

    user = relationship("User", back_populates="score_history")


class AdvisorSession(Base):
    """Stores each AI advisor consultation for history/audit."""
    __tablename__ = "advisor_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    input_snapshot = Column(Text, nullable=False)   # JSON string of the metrics sent to Gemini
    ai_analysis = Column(Text, nullable=False)       # free-text analysis
    action_plan = Column(Text, nullable=False)       # JSON string: list of 5 steps
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    user = relationship("User", back_populates="advisor_sessions")
