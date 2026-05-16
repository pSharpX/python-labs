from pydantic import BaseModel, Field, ConfigDict


class ProfileData(BaseModel):
    first_name: str = Field(serialization_alias="firstName")
    last_name: str = Field(serialization_alias="lastName")
    email: str
    login: str
    mobile_phone: str = Field(serialization_alias="mobilePhone")

    model_config = ConfigDict(serialize_by_alias=True)

class CreateUser(BaseModel):
    profile: ProfileData

    @classmethod
    def create(cls, email: str, first_name: str, last_name: str, phone: str):
        return cls(
            profile=ProfileData(
                first_name=first_name,
                last_name=last_name,
                email=email,
                login=email,
                mobile_phone=phone
            )
        )