"""
SQLAlchemy is a database wrapper, ORM wrapper
    - needs a DB driver, in our case ... that connects to Postgresql 
    - whatever we creata a connection using sqlalchemy we need 2 things
        - an engine, an engine is a something where we pass our databse credentials to 
        - when we have an engine, we create a session  from that engine
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

'''
commands to run 
 
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -i -u postgres
psql
- list databases, by default you have postgres, template0 and template1 databases

'''

from local_settings import postgresql as settings

def get_engine(user, password, host, port, db):
    url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    if not database_exists(url):
        create_database(url)

    engine = create_engine(url, pool_size = 50, echo = True)

    return engine

engine = get_engine(
    settings['pguser'],
    settings['pgpassword'],
    settings['pghost'],
    settings['pgport'],
    settings['pgdb']
)

engine.url