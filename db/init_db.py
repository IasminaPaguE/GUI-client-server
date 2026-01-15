'''
This module initializes the database by creating all necessary tables
This file creates the database connection using the create_engine function
This file uses SQLAlchemy to define the database schema and create tables

'''

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from transfer_metrics_model import Base


def _get_connection():
        load_dotenv()
        
        user = os.environ["POSTGRES_USER"]
        password = os.environ["POSTGRES_PASSWORD"]
        db = os.environ["POSTGRES_DB"]
        

        url = f"postgresql+psycopg2://{user}:{password}@localhost:5432/{db}"
        return create_engine(url, echo=True, pool_pre_ping=True)

def init_db():
    engine = _get_connection()
    
    

    # Create all tables in the database
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()


