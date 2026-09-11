from sqlalchemy import Column, String, Numeric, Text, BigInteger

from src.catalog.models.model_base import Base


class BlendedRateModel(Base):
    __tablename__ = 'blended_rate'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_type = Column(String(150), nullable=False)
    smb_rate = Column(Numeric(10, 2), nullable=False)
    corporate_rate = Column(Numeric(10, 2), nullable=False)
    suggested_use = Column(Text)