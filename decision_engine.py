import joblib
import numpy as np
import pandas as pd

# Load the trained model once when this file is imported
model = joblib.load("credit_model.pkl")


def run_rules_engine(applicant: dict) -> dict:
    """Threshold-driven: hard business rules only."""
    
    reasons = []
    decision = "APPROVE"

    if applicant["credit_score"] < 580:
        decision = "REJECT"
        reasons.append("credit_score below 580")

    if applicant["debt_to_income"] > 0.55:
        decision = "REJECT"
        reasons.append("debt_to_income above 55%")

    if applicant["loan_amount"] > applicant["income"] * 0.6:
        decision = "REJECT"
        reasons.append("loan_amount exceeds 60% of income")

    if decision == "APPROVE" and applicant["debt_to_income"] > 0.40:
        decision = "REVIEW"
        reasons.append("debt_to_income borderline (40-55%)")

    return {
        "decision": decision,
        "rule_triggered": reasons if reasons else ["no rules triggered"],
        "model_score": None
    }


def run_model_engine(applicant: dict) -> dict:
    """Model-driven: logistic regression score drives decision."""

    features = pd.DataFrame([{
    "income": applicant["income"],
    "credit_score": applicant["credit_score"],
    "debt_to_income": applicant["debt_to_income"],
    "loan_amount": applicant["loan_amount"]
    }])

    prob_default = model.predict_proba(features)[0][1]  # P(default)

    if prob_default >= 0.65:
        decision = "REJECT"
    elif prob_default >= 0.35:
        decision = "REVIEW"
    else:
        decision = "APPROVE"

    return {
        "decision": decision,
        "rule_triggered": ["model-driven — no rules applied"],
        "model_score": round(float(prob_default), 4)
    }


def make_decision(applicant: dict, mode: str = "model") -> dict:
    """Master toggle — routes to rules or model engine."""

    if mode == "rules":
        result = run_rules_engine(applicant)
    elif mode == "model":
        result = run_model_engine(applicant)
    else:
        raise ValueError(f"Unknown mode: {mode}. Use 'rules' or 'model'.")

    result["mode"] = mode
    result["applicant"] = applicant
    return result