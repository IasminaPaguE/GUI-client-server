import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _create_engine():
    load_dotenv()
        
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
        

    url = f"postgresql+psycopg2://{user}:{password}@localhost:5432/{db}"
    return create_engine(url, echo=True, pool_pre_ping=True)

def create_session_maker():
    engine = _create_engine()
    Session = sessionmaker(engine)

def create_session(self, metrics):
    with Session.begin() as session:
        session.add(some_object)



