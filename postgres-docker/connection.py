from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, CHAR
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

Base = declarative_base()

class Person(Base):
    __tablename__ = "people" #this is the table name inside of the DB, inside the SQLite DB in our case

    ssn = Column("ssn", Integer, primary_key=True)
    firstname = Column("firstname", String)
    lastname = Column("lastname", String)
    gender = Column("gender",CHAR)
    age = Column("age", Integer)

    def __init__(self,ssn, firstname, lastname, gender, age):
        self.ssn = ssn
        self.firstname = firstname
        self.lastname = lastname
        self.gender = gender
        self.age = age

    def __repr__(self):
        """
        This function is used to customize how we want to print a person attributes
        """
        return f"({self.ssn}), {self.firstname}, {self.lastname}, ({self.gender}, {self.age})"
    
def get_connection():
    load_dotenv()
    
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    db = os.environ["POSTGRES_DB"]
    

    url = f"postgresql+psycopg2://{user}:{password}@localhost:5432/{db}"
    return create_engine(url, echo=True, pool_pre_ping=True)
   

if __name__ == '__main__':

    try:
        # GET THE CONNECTION OBJECT (ENGINE) FOR THE DATABASE
        engine = get_connection()
        print(
            f"Connection to the host localhost for user ${{POSTGRES_USER}} created successfully.")
    except Exception as ex:
        print("Connection could not be made due to the following error: \n", ex)

    engine = get_connection()
    with engine.connect() as conn:
        print("Connected OK!")

    Base.metadata.create_all(bind = engine)

    Session = sessionmaker(bind = engine) 
    session = Session()

    person1 = Person(12345, "Iasmina", "Pagu", "M", 22)
    person2 = Person(12348, "aaa", "aaa", "M", 22)
    person3 = Person(12349, "bbb", "bbb", "M", 22)
    person4 = Person(12340, "bbaa", "bbaa", "M", 22)
    session.add(person1)
    session.add(person2)
    session.add(person3)
    session.add(person4)


    session.commit() 


    results = session.query(Person).all() 
    print(results)



