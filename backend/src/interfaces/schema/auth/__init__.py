from pydantic import BaseModel, Field, EmailStr, model_validator
from email_validator import validate_email
from fastapi import HTTPException
from src.utils import is_strong_pass


class SignUp(BaseModel):
    username: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=8, max_length=30)
    email: EmailStr = Field(..., min_length=12, max_length=255)

    @model_validator(mode='after')
    def validate_email(self):
        emailinfo = validate_email(self.email, check_deliverability=True)

        email = emailinfo.normalized
        self.email = email
        return self

    @model_validator(mode='after')
    def validate_password(self):
        if not is_strong_pass(self.password):
            raise HTTPException(
                status_code=400, detail='Password is not strong enough'
            )
        return self


class SignIn(BaseModel):
    username: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=8, max_length=30)
