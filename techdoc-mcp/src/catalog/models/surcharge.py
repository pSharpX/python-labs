from sqlalchemy import Column, String, Numeric, Text

from src.catalog.models.model_base import Base


class SurchargeModel(Base):
    __tablename__ = 'surcharge'

    code = Column(String(20), primary_key=True)
    condition = Column(String(150), nullable=False)
    factor = Column(Numeric(5, 2), nullable=False)
    rule = Column(Text)