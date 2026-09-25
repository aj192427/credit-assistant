"""
Pure calculation helpers for credit metrics. Kept separate from the DB layer
so they're easy to unit test.
"""
from app.models import band_for_score, CreditBand


def calc_debt_to_income(total_debt: float, monthly_income: float) -> float:
    """
    DTI ratio as a percentage. Uses total outstanding debt against monthly income,
    which is the common simplified metric Indian lenders quote to consumers
    (a stricter version would use monthly EMI outflow / monthly income).
    """
    if monthly_income <= 0:
        return 0.0
    return round((total_debt / monthly_income) * 100, 2)


def calc_utilization(credit_used: float, total_credit_limit: float) -> float:
    """Credit utilization ratio as a percentage."""
    if total_credit_limit <= 0:
        return 0.0
    return round((credit_used / total_credit_limit) * 100, 2)


def get_band(score: int) -> CreditBand:
    return band_for_score(score)


def recalculate_profile_fields(
    credit_score: int,
    monthly_income: float,
    total_debt: float,
    credit_used: float,
    total_credit_limit: float,
) -> dict:
    """Returns the derived fields that should be persisted alongside raw inputs."""
    return {
        "debt_to_income_ratio": calc_debt_to_income(total_debt, monthly_income),
        "utilization_ratio": calc_utilization(credit_used, total_credit_limit),
        "credit_band": get_band(credit_score),
    }
