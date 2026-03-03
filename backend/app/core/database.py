from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine=create_engine(settings.DATABASE_URL,
                      connect_args={"check_same_thread": False})

SessionaLocal=sessionmaker(autocommit=False,
                            autoflush=False, 
                            bind=engine)
Base=declarative_base()

def get_db():
    db=SessionaLocal()
    try:
        yield db
    finally:
        db.close()