"""
Pydantic request/response schemas.
"""
import datetime as dt
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import CreditBand


# ---------- Auth / User ----------

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    created_at: dt.datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Credit Profile ----------

class CreditProfileIn(BaseModel):
    """Input payload for onboarding / updating financial data (Scenario 1 & 4)."""
    credit_score: int = Field(..., ge=300, le=900)
    monthly_income: float = Field(..., gt=0)
    monthly_expenses: float = Field(..., ge=0)
    total_debt: float = Field(0, ge=0)
    total_credit_limit: float = Field(0, ge=0)
    credit_used: float = Field(0, ge=0)
    missed_payments_last_year: int = Field(0, ge=0)


class CreditProfileOut(BaseModel):
    credit_score: int
    monthly_income: float
    monthly_expenses: float
    total_debt: float
    total_credit_limit: float
    credit_used: float
    missed_payments_last_year: int
    debt_to_income_ratio: float
    utilization_ratio: float
    credit_band: CreditBand
    updated_at: dt.datetime

    class Config:
        from_attributes = True


class ScoreHistoryPoint(BaseModel):
    credit_score: int
    utilization_ratio: float
    debt_to_income_ratio: float
    recorded_at: dt.datetime

    class Config:
        from_attributes = True


class DashboardOut(BaseModel):
    """Everything the dashboard needs in a single call: current snapshot + trend + deltas."""
    profile: CreditProfileOut
    history: List[ScoreHistoryPoint]
    score_delta: Optional[int] = None          # change vs previous snapshot
    utilization_delta: Optional[float] = None  # change vs previous snapshot


# ---------- AI Advisor ----------

class AdvisorRequest(BaseModel):
    """Optional free-text goal from the user, e.g. 'I want to buy a car in 12 months'."""
    goal: Optional[str] = Field(None, max_length=500)


class AdvisorResponse(BaseModel):
    analysis: str
    action_plan: List[str]
    credit_band: CreditBand
    generated_at: dt.datetime


class AdvisorChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=1200)


class AdvisorChatRequest(BaseModel):
    messages: List[AdvisorChatMessage] = Field(..., min_length=1, max_length=12)


class AdvisorChatResponse(BaseModel):
    reply: str
