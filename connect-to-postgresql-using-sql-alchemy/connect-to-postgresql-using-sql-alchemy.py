from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, CHAR, text
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()

"""
this call is going to return a class

declarative_base is a factory function that creates a base class for your ORM models in SQLAlchemy.
All classes that inherit from Base are automatically mapped to database tables and share Base.metadata, 
which you can use to create the tables:

A “factory function” is just a normal function whose main job is to create and return objects
(often of a particular type or with some configuration), 
instead of you calling the class constructor directly.

In other words:
You call the function → it builds/configures something → it returns the ready‑to‑use object.


EX:
class User:
    def __init__(self, name, is_admin=False):
        self.name = name
        self.is_admin = is_admin

def create_admin(name):  # factory function
    return User(name=name, is_admin=True)

admin = create_admin("Alice")  # returns a User configured as admin
"""


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
        return f"{self.ssn}, {self.firstname}, {self.lastname}, {self.gender}, {self.age}"

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


engine = create_engine("sqlite:///mydb.db", echo = True) #we are going to have an in-memory db, that is going to store all this information
#in the RAM and restore that information everytime we run our program
#in this example, we are going to store the info in a dedicated file, named mydb.db

'''
The start of any SQLAlchemy application is an object called the Engine. 
This object acts as a central source of connections to a particular database, 
providing both a factory as well as a holding space called a connection pool for 
these database connections. The engine is typically a global object created just once for a particular database server, 
and is configured using a URL string which will describe how it should connect to the database host or backend.
'''

Base.metadata.create_all(bind = engine)
"""
It takes all the classes that extend from the Base class and creates them in the DB
So, it connects to the engines and creates all of these tables, so the Person table is going to be created after we run this line of code
"""

Session = sessionmaker(bind = engine) #the class
session = Session() #the instance, we are calling the constructor

person1 = Person(12345, "Iasmina", "Pagu", "M", 22)
person2 = Person(12348, "aaa", "aaa", "M", 22)
person3 = Person(12349, "bbb", "bbb", "M", 22)
session.add(person1)
session.add(person2)
session.add(person3)


thing1 = Thing(1, "car", person1.ssn)
thing2 = Thing(2, "car2", person1.ssn)
thing3 = Thing(3, "car3", person3.ssn)
thing4 = Thing(3, "car4", person2.ssn)
session.add(thing1)
session.add(thing2)
session.add(thing3)


session.commit() #this is going to commit the changes to the DB


results = session.query(Person).all() #select * from Person
print(results)

filtered_results = session.query(Person).filter(Person.firstname == "Iasmina").all()
print(filtered_results)


'''
That message is coming from the type checker (Pylance/Pyright)
In SQLAlchemy’s type stubs, the mapped attribute (like firstname) is modeled as a generic descriptor

When you access that generic attribute through the class (Person.firstname) instead of an instance, 
the type checker can’t decide whether it should treat it as an instance attribute or as a class attribute,
so it calls the access “ambiguous”.

At runtime, SQLAlchemy defines Person.firstname as a special descriptor that builds SQL expressions, 
so using it in filters is exactly what you’re supposed to do.
'''

'''
Without .all(), no SQL is executed yet and filtered_results is just a Query object, 
not a list of Person rows.
This actually runs the SQL, fetches all matching rows from the database, 
and returns a Python list of Person instances.

filtered_results is a lazy query object; the DB isn’t hit until you:

- iterate over it: for p in filtered_results: ...
- force evaluation: list(filtered_results), .all(), .first(), .one(), etc.
So if you just print(filtered_results) without .all(), you’ll see a representation of the query, not the actual rows.
Demonstration:
for the call : filtered_results = session.query(Person).filter(Person.firstname == "Iasmina")
the equivalent SQL query is:
SELECT people.ssn AS people_ssn, people.firstname AS people_firstname, people.lastname AS people_lastname, people.gender AS people_gender, people.age AS people_age
FROM people
WHERE people.firstname = ?

and if you add the .all()at the end, you will get 2 extra lines in the output:
2026-01-12 12:30:52,352 INFO sqlalchemy.engine.Engine [generated in 0.00033s] ('Iasmina',)
[12345, Iasmina, Pagu, M, 22] 

'''

'''
Who executes it?

Your Python code builds a Query (session.query(...).filter(...)).
SQLAlchemy’s ORM compiles that Query to SQL and sends it to the SQLAlchemy Engine.
The Engine uses the underlying DBAPI driver (for SQLite, the built‑in sqlite3 module) to send that SQL string + parameters to the database.
The database server (SQLite) executes the SQL and returns rows.
SQLAlchemy takes those rows and turns them into Person objects (for ORM queries).

'''

'''give me all the things that are from person1'''

results2 = session.query(Thing).filter(Thing.owner == person1.ssn).all()
print(results2)


