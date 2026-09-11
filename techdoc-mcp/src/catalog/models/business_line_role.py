from sqlalchemy import Column, String, Text, BigInteger

from src.catalog.models.model_base import Base


class BusinessLineRoleModel(Base):
    __tablename__ = 'business_line_role'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    business_line = Column(String(150), nullable=False)
    main_role = Column(String(150))
    main_role_code = Column(String(100))
    support_roles = Column(Text)
    target_segment = Column(String(100))
    usage_description = Column(Text)