from sqlalchemy import Column, Integer, Float, String, DateTime, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database import Base, engine

# Step 1: Define the audit log table
class DecisionLog(Base):
    __tablename__ = "decisions_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, nullable=True)  # None if walk-in (not in DB)
    income = Column(Float)
    credit_score = Column(Integer)
    debt_to_income = Column(Float)
    loan_amount = Column(Float)
    model_score = Column(Float, nullable=True)      # None if rules mode
    rule_triggered = Column(String)
    final_decision = Column(String)
    mode = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Step 2: Create the table in PostgreSQL
def create_log_table():
    Base.metadata.create_all(engine)
    print("decisions_log table created.")


# Step 3: Write one decision to the log
SessionLocal = sessionmaker(bind=engine)

def log_decision(applicant: dict, result: dict, applicant_id: int = None):
    session = SessionLocal()

    entry = DecisionLog(
        applicant_id=applicant_id,
        income=applicant["income"],
        credit_score=applicant["credit_score"],
        debt_to_income=applicant["debt_to_income"],
        loan_amount=applicant["loan_amount"],
        model_score=result.get("model_score"),
        rule_triggered=str(result.get("rule_triggered")),
        final_decision=result["decision"],
        mode=result["mode"],
        timestamp=datetime.utcnow()
    )

    session.add(entry)
    session.commit()
    session.close()


# Step 4: Query the log — useful for edge case analysis
def get_edge_cases():
    session = SessionLocal()

    # Find all applicants where rules and model would disagree
    # We stored mode in log — pull all decisions and find same applicant decided differently
    results = session.execute(
        text("SELECT * FROM decisions_log ORDER BY timestamp DESC LIMIT 20")
    ).fetchall()

    session.close()
    return results


if __name__ == "__main__":
    create_log_table()