from pydantic import BaseModel, Field, ConfigDict


class ProfileData(BaseModel):
    first_name: str = Field(serialization_alias="firstName")
    last_name: str = Field(serialization_alias="lastName")
    email: str
    login: str
    mobile_phone: str = Field(serialization_alias="mobilePhone")

    model_config = ConfigDict(serialize_by_alias=True)

class PasswordValue(BaseModel):
    value: str = Field()

class CredentialsData(BaseModel):
    password: PasswordValue

    model_config = ConfigDict(serialize_by_alias=True)

class CreateUser(BaseModel):
    profile: ProfileData
    credentials: CredentialsData | None

    @classmethod
    def create(cls, email: str, first_name: str, last_name: str, phone: str):
        return cls(
            profile=ProfileData(
                first_name=first_name,
                last_name=last_name,
                email=email,
                login=email,
                mobile_phone=phone
            ),
            credentials=None
        )

    @classmethod
    def create_with_credentials(cls, email: str, first_name: str, last_name: str, phone: str, credentials: str):
        return cls(
            profile=ProfileData(
                first_name=first_name,
                last_name=last_name,
                email=email,
                login=email,
                mobile_phone=phone
            ),
            credentials=CredentialsData(
                password=PasswordValue(value=credentials),
            )
        )