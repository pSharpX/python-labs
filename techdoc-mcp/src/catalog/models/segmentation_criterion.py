from sqlalchemy import Column, String, Text, BigInteger

from src.catalog.models.model_base import Base


class SegmentationCriterionModel(Base):
    __tablename__ = 'segmentation_criterion'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    criterion = Column(String(150), nullable=False)
    smb_description = Column(Text)
    corporate_description = Column(Text)