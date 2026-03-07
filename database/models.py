"""Модели базы данных."""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class LLMLog(Base):
    """Лог запросов и ответов LLM."""

    __tablename__ = "llm_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    chat_id = Column(Integer, nullable=True, index=True)
    ai_provider = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    prompt_type = Column(String(50), nullable=True)
    duration_sec = Column(Float, nullable=True)

    def __repr__(self):
        return (
            f"<LLMLog(id={self.id}, provider={self.ai_provider}, "
            f"type={self.prompt_type}, time={self.timestamp})>"
        )