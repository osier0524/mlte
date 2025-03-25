from mlte.backend.db.config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mlte.backend.db.models import Base

# Connect to the database
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized.")