from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, CHAR
from sqlalchemy.orm import sessionmaker, declarative_base


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

class Thing(Base):
    __tablename__ = "things"

    tid = Column("tid", Integer, primary_key= True)
    description = Column("description", String)
    owner = Column("owner", Integer, ForeignKey("people.ssn")) #we are using the table name, not the object name or something else


    def __init__(self, tid, description, owner):
        self.tid = tid
        self.description = description
        self.owner = owner

    def __repr__(self):
        return f'{self.tid}, {self.description}, owned by {self.owner}'




engine = create_engine("sqlite:///mydb.db", echo = True) 

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


thing1 = Thing(1, "car", person1.ssn)
thing2 = Thing(2, "car2", person1.ssn)
thing3 = Thing(3, "car3", person3.ssn)
thing4 = Thing(3, "car4", person2.ssn)
session.add(thing1)
session.add(thing2)
session.add(thing3)

session.commit() 


results = session.query(Person).all() 
print(results)

filtered_results = session.query(Person).filter(Person.firstname == "Iasmina").all()
print(filtered_results)

filtered_results2 = session.query(Person).filter(Person.firstname.like("%b%")).all()
print(filtered_results2)
print(type(filtered_results2))


filtered_results3 = session.query(Person).filter(Person.firstname.in_(["aaa", "Iasmina"])).all()
print(filtered_results3)



results2 = session.query(Thing).filter(Thing.owner == person1.ssn).all()
print(results2)
