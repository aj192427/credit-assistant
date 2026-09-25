"""
Wraps calls to Google's Gemini API to produce the AI financial consultation
described in Scenario 2: an analysis of the user's credit health plus a
5-step actionable plan tailored to Indian banking norms (CIBIL score bands,
RBI-relevant conventions, common Indian lenders/products).
"""
import json
import logging

from app.config import settings
from app.models import CreditBand

logger = logging.getLogger(__name__)

_SYSTEM_INSTRUCTION = """You are a credit health advisor for Indian consumers.
You understand CIBIL/Experian/Equifax score bands (300-900), RBI lending norms,
typical Indian credit products (credit cards, personal loans, home loans, gold loans),
and realistic debt-to-income and credit-utilization targets.

Always respond with STRICT JSON only, no markdown, no commentary, in this exact shape:
{
  "analysis": "<2-4 sentence plain-English analysis of the user's credit health>",
  "action_plan": ["<step 1>", "<step 2>", "<step 3>", "<step 4>", "<step 5>"]
}
The action_plan must contain exactly 5 concrete, specific, prioritized steps the
user can take, referencing their actual numbers where useful (e.g. utilization %,
DTI %, missed payments). Keep each step to one sentence.
"""


def _build_prompt(metrics: dict, goal: str | None) -> str:
    goal_line = f"\nThe user's stated goal: {goal}" if goal else ""
    return (
        f"User's financial snapshot (India):\n"
        f"- Credit score: {metrics['credit_score']} ({metrics['credit_band']})\n"
        f"- Monthly income: INR {metrics['monthly_income']:.2f}\n"
        f"- Monthly expenses: INR {metrics['monthly_expenses']:.2f}\n"
        f"- Total outstanding debt: INR {metrics['total_debt']:.2f}\n"
        f"- Debt-to-income ratio: {metrics['debt_to_income_ratio']:.2f}%\n"
        f"- Credit utilization: {metrics['utilization_ratio']:.2f}%\n"
        f"- Missed payments (last 12 months): {metrics['missed_payments_last_year']}"
        f"{goal_line}\n\n"
        "Analyze this and produce the JSON response described in your instructions."
    )


def get_ai_consultation(metrics: dict, goal: str | None = None) -> dict:
    """
    Calls Gemini with the user's metrics and returns a dict:
    {"analysis": str, "action_plan": [str, str, str, str, str]}

    Falls back to a deterministic rule-based response if no API key is configured
    or the call fails, so the app remains usable without a live Gemini key.
    """
    if not settings.gemini_api_key:
        logger.warning("GEMINI_API_KEY not set; using fallback advisor logic.")
        return _fallback_consultation(metrics, goal)

    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=_SYSTEM_INSTRUCTION,
        )
        prompt = _build_prompt(metrics, goal)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        data = json.loads(response.text)
        action_plan = data.get("action_plan", [])[:5]
        while len(action_plan) < 5:
            action_plan.append("Continue monitoring your credit report monthly for errors.")
        return {"analysis": data.get("analysis", "").strip(), "action_plan": action_plan}
    except Exception:
        logger.exception("Gemini call failed; using fallback advisor logic.")
        return _fallback_consultation(metrics, goal)


def _fallback_consultation(metrics: dict, goal: str | None = None) -> dict:
    """Deterministic rule-based plan, used when Gemini is unavailable."""
    band = metrics["credit_band"]
    util = metrics["utilization_ratio"]
    dti = metrics["debt_to_income_ratio"]
    missed = metrics["missed_payments_last_year"]
    goal_text = (goal or "").strip()
    goal_lower = goal_text.lower()

    analysis = (
        f"Your credit score falls in the '{band}' band with {util:.1f}% utilization "
        f"and a {dti:.1f}% debt-to-income ratio. "
        + ("Missed payments are actively hurting your score. " if missed > 0 else "")
        + "Focus on lowering utilization and maintaining a clean payment history to move up a band."
    )

    if goal_text:
        analysis = f"For your goal of '{goal_text}', {analysis[0].lower() + analysis[1:]}"

    if any(word in goal_lower for word in ("car", "vehicle", "bike", "automobile")):
        steps = [
            "Set a monthly vehicle budget that includes the EMI, insurance, fuel, maintenance, and an emergency buffer.",
            "Build the down payment in a separate savings account and avoid using a credit card or personal loan for it.",
            f"Improve your lender profile by keeping utilization under 30% and reducing your current {dti:.1f}% debt-to-income ratio before applying.",
            "Request loan quotes from a small number of lenders within a short window and compare the total repayment cost, not only the EMI.",
            "Avoid new credit applications and keep every existing EMI and card payment on time until the vehicle loan is approved.",
        ]
    elif any(word in goal_lower for word in ("home", "house", "flat", "property", "mortgage")):
        steps = [
            "Set a home price limit where the expected EMI keeps your total debt-to-income ratio below 40%.",
            "Build the down payment, registration costs, and at least six months of EMIs before applying for a home loan.",
            f"Lower your current {dti:.1f}% debt-to-income ratio by paying down expensive debt before seeking pre-approval.",
            "Keep utilization under 30% and avoid closing long-standing accounts while preparing your credit profile.",
            "Compare pre-approval offers by interest rate, processing fees, insurance requirements, and total repayment amount.",
        ]
    elif any(word in goal_lower for word in ("loan", "borrow", "financ", "emi")):
        steps = [
            f"Choose an EMI that keeps your debt-to-income ratio near or below 40%, rather than borrowing the maximum offered.",
            "Pay down high-interest balances first so the new loan does not increase your monthly obligations unnecessarily.",
            "Keep credit utilization under 30% and do not submit multiple loan applications at the same time.",
            "Compare the annual interest rate, processing fee, foreclosure terms, and total repayment across lenders.",
            "Set up automatic EMI payments and keep a one-month installment buffer in your bank account.",
        ]
    elif any(word in goal_lower for word in ("debt", "pay off", "repay", "repayment")):
        steps = [
            "List every balance, interest rate, minimum payment, and due date, then direct extra money to the highest-interest debt.",
            f"Target a debt-to-income ratio below 40% by avoiding new borrowing while paying down your current balances.",
            "Keep at least a small emergency buffer so unexpected costs do not become new card debt.",
            "Keep every account current with automatic minimum payments and make extra payments immediately after payday.",
            "Review your progress monthly and redirect each cleared EMI toward the next balance.",
        ]
    elif any(word in goal_lower for word in ("score", "cibil", "credit health", "improve credit")):
        steps = [
            f"Bring utilization from {util:.1f}% to under 30% and preferably below 10% before the monthly statement date.",
            "Pay every EMI and card bill on time using automatic payments and calendar reminders.",
            "Avoid multiple new credit applications because each hard inquiry can affect your score.",
            "Keep older credit accounts open when they have no unnecessary fees to preserve account history.",
            "Check your CIBIL, Experian, or Equifax report every three months and dispute inaccurate entries.",
        ]
    elif any(word in goal_lower for word in ("card", "utilization", "limit")):
        steps = [
            f"Pay down card balances to reduce utilization from {util:.1f}% to below 30% before the statement date.",
            "Split large purchases across billing cycles or use savings instead of increasing revolving balances.",
            "Request a limit increase only when you can avoid new spending and the lender does not require multiple applications.",
            "Pay the full statement balance automatically to avoid interest and missed-payment marks.",
            "Review each card quarterly and close only accounts with costly fees after considering their age and utilization impact.",
        ]
    elif any(word in goal_lower for word in ("save", "saving", "emergency", "fund")):
        steps = [
            "Automate a fixed transfer to savings on payday before discretionary spending begins.",
            "Build an emergency fund covering at least three to six months of essential expenses.",
            "Keep the emergency fund separate from your credit card repayment and down-payment goals.",
            "Avoid new borrowing for planned purchases while the savings target is still in progress.",
            "Review the goal monthly and increase the transfer after every salary increase or cleared debt payment.",
        ]
    else:
        steps = [
            "Define the target amount and deadline, then convert it into a monthly savings target you can track.",
            f"Keep utilization under 30% and work to reduce your current {dti:.1f}% debt-to-income ratio before taking new credit.",
            "Maintain automatic payments for every EMI and credit card bill to protect your payment history.",
            "Keep an emergency buffer so the goal does not require expensive short-term borrowing.",
            "Review your credit report and progress monthly, adjusting the plan when your income or expenses change.",
        ]

    return {"analysis": analysis, "action_plan": steps}
