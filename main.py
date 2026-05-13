from fastapi import FastAPI, Query
from pydantic import BaseModel
from audit_log import log_decision
import os
import joblib
import pandas as pd
from sqlalchemy import text


# Train model on startup if .pkl doesn't exist
if not os.path.exists("credit_model.pkl"):
    print("Model not found — training now...")
    from database import engine
    from sklearn.linear_model import LogisticRegression

    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM applicants"), conn)

    X = df[["income", "credit_score", "debt_to_income", "loan_amount"]]
    y = df["label"]

    model = LogisticRegression()
    model.fit(X, y)
    joblib.dump(model, "credit_model.pkl")
    print("Model trained and saved.")

# Now safe to import decision engine (pkl exists)
from decision_engine import make_decision


app = FastAPI(
    title="Credit Risk Decisioning Simulator",
    description="Simulates loan decisioning using rule-based and model-driven strategies. Built with Python, FastAPI, PostgreSQL, and Scikit-learn.",
    version="1.0.0"
)


class ApplicantInput(BaseModel):
    income: float
    credit_score: int
    debt_to_income: float
    loan_amount: float
    applicant_id: int = None

    class Config:
        json_schema_extra = {
            "example": {
                "income": 75000,
                "credit_score": 680,
                "debt_to_income": 0.35,
                "loan_amount": 20000
            }
        }


@app.get("/")
def root():
    return {
        "status": "running",
        "project": "Credit Risk Decisioning Simulator",
        "endpoints": ["/decide", "/docs"]
    }


@app.post("/decide")
def decide(
    applicant: ApplicantInput,
    mode: str = Query(default="model", enum=["model", "rules"])
):
    applicant_dict = {
        "income": applicant.income,
        "credit_score": applicant.credit_score,
        "debt_to_income": applicant.debt_to_income,
        "loan_amount": applicant.loan_amount
    }

    result = make_decision(applicant_dict, mode=mode)
    log_decision(applicant_dict, result, applicant_id=applicant.applicant_id)

    return {
        "decision": result["decision"],
        "model_score": result["model_score"],
        "rule_triggered": result["rule_triggered"],
        "mode": mode,
        "applicant": applicant_dict,
        "audit": "logged to PostgreSQL"
    }