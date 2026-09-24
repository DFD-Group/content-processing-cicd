import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session