from email_validator import validate_email
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field, model_validator
from src.utils import is_strong_pass


class SignUp(BaseModel):
    name: str = Field(..., min_length=5, max_length=255)
    email: EmailStr = Field(..., min_length=12, max_length=255)
    phone: str = Field(..., min_length=8, max_length=21)
    document: str = Field(..., min_length=11, max_length=20)
    username: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=8, max_length=30)

    def model_post_init(self, __context):
        self.email = self.email.lower()
        self.name = self.name.lower()
        self.username = self.username.lower()
        self.document = self.document.replace('.', '').replace('-', '')
        self.phone = (
            self.phone.replace('-', '').replace(' ', '').replace('+', '')
        )

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
