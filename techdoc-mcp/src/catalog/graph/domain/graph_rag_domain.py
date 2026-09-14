from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TargetSegment(str, Enum):
    SMB = "smb"
    CORPORATE = "corporate"


class BusinessLineNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Name of the business line")


class ProductServiceDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    business_line: str = Field(description="Associated Business Line name")
    family: str = Field(description="Associated Family name")
    product_code: str = Field(description="Unique code identifying the product/service")
    product_name: str = Field(description="Display name of the product/service")
    type: str = Field(description="Category type of service e.g., Assessment, Migration")
    smb_applicable: bool = Field(description="Indicates if offered to SMB segment")
    corp_applicable: bool = Field(description="Indicates if offered to Corporate segment")
    description: Optional[str] = Field(default=None, description="Detailed scope description")


class HourlyRateDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    role_code: str = Field(description="Unique identifier for the role rate")
    category: Optional[str] = Field(default=None, description="Functional domain category")
    position: str = Field(description="Job title/role name")
    level: str = Field(description="Seniority level e.g., Junior, Mid, Senior")
    smb_rate: float = Field(description="Hourly rate for SMB clients")
    corporate_rate: float = Field(description="Hourly rate for Corporate clients")
    description: Optional[str] = Field(default=None, description="Scope of responsibilities")


class RoleRequirement(BaseModel):
    model_config = ConfigDict(frozen=True)

    role: str = Field(description="Position title")
    rate: float = Field(description="Applicable hourly rate")


class ServiceFootprintDTO(BaseModel):
    model_config = ConfigDict(frozen=True)

    product_code: str
    product_name: str
    product_description: Optional[str] = None
    family: str
    business_line: str
    associated_roles: List[RoleRequirement] = Field(default_factory=list)
