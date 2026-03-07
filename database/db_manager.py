"""Менеджер базы данных."""

import time
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, LLMLog


class DatabaseManager:
    """Управляет подключением к БД и логированием."""

    def __init__(self, db_url: str = "sqlite:///cities_bot.db"):
        self._engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(bind=self._engine)
        print(f"✅ База данных инициализирована: {db_url}")

    def get_session(self) -> Session:
        """Создаёт новую сессию."""
        return self._session_factory()

    def log_request(
        self,
        ai_provider: str,
        prompt: str,
        response: str,
        chat_id: Optional[int] = None,
        prompt_type: Optional[str] = None,
        duration_sec: Optional[float] = None,
    ) -> None:
        """Сохраняет запрос и ответ в БД."""
        session = self.get_session()
        try:
            log_entry = LLMLog(
                chat_id=chat_id,
                ai_provider=ai_provider,
                prompt=prompt,
                response=response,
                prompt_type=prompt_type,
                duration_sec=duration_sec,
            )
            session.add(log_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"  ❌ Ошибка записи в БД: {e}")
        finally:
            session.close()

    def get_logs_count(self) -> int:
        """Возвращает количество записей."""
        session = self.get_session()
        try:
            return session.query(LLMLog).count()
        finally:
            session.close()

    def get_logs_by_chat(self, chat_id: int, limit: int = 50) -> list[LLMLog]:
        """Возвращает логи конкретного чата."""
        session = self.get_session()
        try:
            return (
                session.query(LLMLog)
                .filter(LLMLog.chat_id == chat_id)
                .order_by(LLMLog.timestamp.desc())
                .limit(limit)
                .all()
            )
        finally:
            session.close()