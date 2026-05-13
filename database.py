from sqlalchemy import create_engine, Column, Integer, Float, String, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Applicant(Base):
    __tablename__ = "applicants"

    applicant_id = Column(Integer, primary_key=True, autoincrement=True)
    income = Column(Float)
    credit_score = Column(Integer)
    debt_to_income = Column(Float)
    loan_amount = Column(Float)
    label = Column(Integer)  # 0 = paid back, 1 = defaulted


def create_tables():
    Base.metadata.create_all(engine)
    print("Tables created successfully.")


if __name__ == "__main__":
    create_tables()