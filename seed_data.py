import pandas as pd
import numpy as np
from database import SessionLocal, Applicant

np.random.seed(42)
n = 50

# Generate realistic applicant data
incomes = np.random.randint(25000, 120000, n)
credit_scores = np.random.randint(520, 800, n)
dtis = np.round(np.random.uniform(0.10, 0.65, n), 2)
loan_amounts = np.random.randint(5000, 40000, n)

# Create labels based on realistic risk logic
# High DTI + low credit score + low income = more likely to default
labels = []
for i in range(n):
    risk_score = 0
    if credit_scores[i] < 580:
        risk_score += 2
    if dtis[i] > 0.45:
        risk_score += 2
    if incomes[i] < 35000:
        risk_score += 1
    if loan_amounts[i] > incomes[i] * 0.5:
        risk_score += 1
    label = 1 if risk_score >= 3 else 0
    labels.append(label)

# Insert into database
session = SessionLocal()

for i in range(n):
    applicant = Applicant(
        income=float(incomes[i]),
        credit_score=int(credit_scores[i]),
        debt_to_income=float(dtis[i]),
        loan_amount=float(loan_amounts[i]),
        label=int(labels[i])
    )
    session.add(applicant)

session.commit()
session.close()

print(f"Inserted 50 applicants.")
print(f"Defaulters (label=1): {sum(labels)}")
print(f"Good payers (label=0): {n - sum(labels)}")