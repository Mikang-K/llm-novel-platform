from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class Novel(Base):
    __tablename__ = "novels"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key = True,
        autoincrement = True
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )