import json
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from core.models.state import State

Base = declarative_base()


class StateModel(Base):
    """SQLAlchemy model for storing State in the database"""
    __tablename__ = "states"
    
    id = Column(String, primary_key=True)
    steps = Column(Integer, default=0)
    status = Column(String, default="running")
    context = Column(JSON, default=list)
    pending_tool_calls = Column(JSON, default=list)
    error = Column(Text, nullable=True)
    final_answer = Column(Text, nullable=True)


# SQLite database (file-based, perfect for development)
# Database file is stored in backend/data/ directory
db_path = Path(__file__).resolve().parent.parent / "data" / "agent_states.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


def pydantic_to_db(state: State) -> StateModel:
    """Convert Pydantic State to database model"""
    return StateModel(
        id=state.id,
        steps=state.steps,
        status=state.status,
        context=state.context,
        pending_tool_calls=state.pending_tool_calls,
        error=state.error,
        final_answer=state.final_answer,
    )


def db_to_pydantic(db_state: StateModel) -> State:
    """Convert database model to Pydantic State"""
    return State(
        id=db_state.id,
        steps=db_state.steps,
        status=db_state.status,
        context=db_state.context or [],
        pending_tool_calls=db_state.pending_tool_calls or [],
        error=db_state.error,
        final_answer=db_state.final_answer,
    )


@contextmanager
def get_db_session():
    """Context manager for database sessions"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

