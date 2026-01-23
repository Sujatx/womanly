from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Create the engine. 
# We use settings.sync_database_url which we defined in config.py
engine = create_engine(settings.sync_database_url, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
