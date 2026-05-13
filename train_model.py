import pandas as pd
import joblib
from sqlalchemy import text
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
from database import engine

# Step 1: Pull data from PostgreSQL into a DataFrame
with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM applicants"), conn)

print(f"Loaded {len(df)} applicants from database.")
print(df.head())

# Step 2: Define features and label
X = df[["income", "credit_score", "debt_to_income", "loan_amount"]]
y = df["label"]

# Step 3: Split into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\nTraining on {len(X_train)} applicants, testing on {len(X_test)}.")

# Step 4: Train the model
model = LogisticRegression()
model.fit(X_train, y_train)
print("\nModel trained successfully.")

# Step 5: See what weights the model learned
feature_names = ["income", "credit_score", "debt_to_income", "loan_amount"]
print("\nWeights the model learned:")
for feature, weight in zip(feature_names, model.coef_[0]):
    print(f"  {feature}: {weight:.6f}")

# Step 6: Test accuracy on the test set
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel accuracy on test set: {accuracy * 100:.1f}%")

# Step 7: Confusion matrix
cm = confusion_matrix(y_test, y_pred)
print(f"\nConfusion Matrix:")
print(f"  True Negatives  (correct approvals):  {cm[0][0]}")
print(f"  False Positives (wrong rejections):    {cm[0][1]}")
print(f"  False Negatives (missed defaulters):   {cm[1][0]}")
print(f"  True Positives  (correct rejections):  {cm[1][1]}")

# Step 8: Save the trained model to a file
joblib.dump(model, "credit_model.pkl")
print("\nModel saved as credit_model.pkl")