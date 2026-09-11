from sqlalchemy import Column, String

from src.catalog.models.model_base import Base


class SpecialtyModel(Base):
    __tablename__ = 'specialty'

    code = Column(String(20), primary_key=True)
    name = Column(String(100), nullable=False)
    code_example = Column(String(100))