import pandas as pd
from sqlalchemy import text
from database import engine
from decision_engine import make_decision
from audit_log import log_decision, get_edge_cases

# Step 1: Pull all 50 applicants from PostgreSQL
with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM applicants"), conn)

print(f"Running decisions on {len(df)} applicants...\n")

rules_correct = 0
model_correct = 0
rules_false_negatives = 0
model_false_negatives = 0

# Step 2: Run every applicant through both modes
for _, row in df.iterrows():
    applicant = {
    "income": float(row["income"]),
    "credit_score": int(row["credit_score"]),
    "debt_to_income": float(row["debt_to_income"]),
    "loan_amount": float(row["loan_amount"])
    }
    actual_label = row["label"]  # 0=good, 1=defaulted

    # Run both modes
    rules_result = make_decision(applicant, mode="rules")
    model_result = make_decision(applicant, mode="model")

    # Log both decisions to PostgreSQL
    log_decision(applicant, rules_result, applicant_id=int(row["applicant_id"]))
    log_decision(applicant, model_result, applicant_id=int(row["applicant_id"]))

    # Track accuracy
    # APPROVE = predicting label 0, REJECT = predicting label 1
    rules_pred = 1 if rules_result["decision"] == "REJECT" else 0
    model_pred = 1 if model_result["decision"] == "REJECT" else 0

    if rules_pred == actual_label:
        rules_correct += 1
    if model_pred == actual_label:
        model_correct += 1

    # Track false negatives (approved a defaulter)
    if actual_label == 1 and rules_pred == 0:
        rules_false_negatives += 1
    if actual_label == 1 and model_pred == 0:
        model_false_negatives += 1

# Step 3: Print accuracy comparison
total = len(df)
print("=" * 50)
print("VALIDATION RESULTS — Rules vs Model")
print("=" * 50)
print(f"Total applicants:        {total}")
print(f"\nRules accuracy:          {rules_correct}/{total} ({rules_correct/total*100:.1f}%)")
print(f"Rules false negatives:   {rules_false_negatives} (approved actual defaulters)")
print(f"\nModel accuracy:          {model_correct}/{total} ({model_correct/total*100:.1f}%)")
print(f"Model false negatives:   {model_false_negatives} (approved actual defaulters)")

# Step 4: Read last 5 log entries from PostgreSQL
print("\n" + "=" * 50)
print("LAST 5 AUDIT LOG ENTRIES (from PostgreSQL)")
print("=" * 50)
recent = get_edge_cases()
for row in recent[:5]:
    print(f"  ID:{row.log_id} | applicant:{row.applicant_id} | "
          f"mode:{row.mode} | decision:{row.final_decision} | "
          f"score:{row.model_score} | time:{row.timestamp}")