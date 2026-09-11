from sqlalchemy import Column, String, Numeric, Text

from src.catalog.models.model_base import Base


class HourlyRateModel(Base):
    __tablename__ = 'hourly_rate'

    role_code = Column(String(20), primary_key=True)
    category = Column(String(100), nullable=False)
    position = Column(String(150), nullable=False)
    level = Column(String(50))
    smb_rate = Column(Numeric(10, 2), nullable=False)
    corporate_rate = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)