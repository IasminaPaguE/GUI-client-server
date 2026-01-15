import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager



load_dotenv()
        
user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]
db = os.environ["POSTGRES_DB"]
        

url = f"postgresql+psycopg2://{user}:{password}@localhost:5432/{db}"

engine = create_engine(url)
SessionLocal = sessionmaker(bind=engine)

@contextmanager
def get_session():
    db = SessionLocal()  # create Session instance
    try:
        yield db          # hand it to the caller
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


