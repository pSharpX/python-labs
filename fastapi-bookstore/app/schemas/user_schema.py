from pydantic import BaseModel, Field, ConfigDict


class UserRegistrationRequest(BaseModel):
    first_name: str = Field(min_length=2, max_length=30)
    last_name: str = Field(min_length=2, max_length=30)
    email: str = Field(min_length=2, max_length=30)
    phone: str = Field(min_length=2, max_length=30)

    model_config = ConfigDict(json_schema_extra = {
            "example": {
                "first_name": "Christian",
                "last_name": "Scot",
                "email": "your_email@email.com",
                "phone": "999999999",
            }
        })
