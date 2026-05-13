from fastapi import FastAPI, Query
from pydantic import BaseModel
from decision_engine import make_decision
from audit_log import log_decision

app = FastAPI(
    title="Credit Risk Decisioning Simulator",
    description="Simulates loan decisioning using rule-based and model-driven strategies. Built with Python, FastAPI, PostgreSQL, and Scikit-learn.",
    version="1.0.0"
)


# Step 1: Define what an applicant request looks like
class ApplicantInput(BaseModel):
    income: float
    credit_score: int
    debt_to_income: float
    loan_amount: float
    applicant_id: int = None  # optional — if pulling from DB

    class Config:
        json_schema_extra = {
            "example": {
                "income": 75000,
                "credit_score": 680,
                "debt_to_income": 0.35,
                "loan_amount": 20000
            }
        }


# Step 2: Health check endpoint — confirms API is running
@app.get("/")
def root():
    return {
        "status": "running",
        "project": "Credit Risk Decisioning Simulator",
        "endpoints": ["/decide", "/docs"]
    }


# Step 3: Main decision endpoint
@app.post("/decide")
def decide(
    applicant: ApplicantInput,
    mode: str = Query(default="model", enum=["model", "rules"])
):
    # Convert to plain dict
    applicant_dict = {
        "income": applicant.income,
        "credit_score": applicant.credit_score,
        "debt_to_income": applicant.debt_to_income,
        "loan_amount": applicant.loan_amount
    }

    # Run decision engine
    result = make_decision(applicant_dict, mode=mode)

    # Log to PostgreSQL
    log_decision(applicant_dict, result, applicant_id=applicant.applicant_id)

    # Return structured response
    return {
        "decision": result["decision"],
        "model_score": result["model_score"],
        "rule_triggered": result["rule_triggered"],
        "mode": mode,
        "applicant": applicant_dict,
        "audit": "logged to PostgreSQL"
    }