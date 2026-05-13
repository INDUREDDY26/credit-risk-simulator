from decision_engine import make_decision

# Test applicants — same edge cases we discussed conceptually
applicants = [
    {
        "name": "John (safe applicant)",
        "income": 95000, "credit_score": 740,
        "debt_to_income": 0.18, "loan_amount": 12000
    },
    {
        "name": "Maria (clear defaulter)",
        "income": 28000, "credit_score": 545,
        "debt_to_income": 0.62, "loan_amount": 22000
    },
    {
        "name": "Dev (edge case — high income, low credit score)",
        "income": 118000, "credit_score": 572,
        "debt_to_income": 0.17, "loan_amount": 15000
    },
    {
        "name": "Sara (edge case — good credit, high DTI)",
        "income": 32000, "credit_score": 715,
        "debt_to_income": 0.51, "loan_amount": 19000
    },
]

print("=" * 60)
print("RULES MODE vs MODEL MODE — SIDE BY SIDE")
print("=" * 60)

for person in applicants:
    name = person.pop("name")  # remove name before passing to engine
    
    rules_result = make_decision(person, mode="rules")
    model_result = make_decision(person, mode="model")

    agree = "✅ AGREE" if rules_result["decision"] == model_result["decision"] else "⚠️  DISAGREE — EDGE CASE"

    print(f"\nApplicant: {name}")
    print(f"  Rules  → {rules_result['decision']}  | Triggered: {rules_result['rule_triggered']}")
    print(f"  Model  → {model_result['decision']}  | P(default): {model_result['model_score']}")
    print(f"  {agree}")