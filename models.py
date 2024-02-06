from sqlalchemy import Date, Column, ForeignKey, Integer, String
from database import Base


class Documents(Base):
    __tablename__ = "Documents"
    id = Column(Integer, primary_key=True)
    path = Column(String(150))
    date = Column(Date)

class Documents_text(Base):
    __tablename__ = "Documents_text"
    id = Column(Integer, primary_key=True)
    id_doc = Column(Integer, ForeignKey("Documents.id", ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    text = Column(String(150))