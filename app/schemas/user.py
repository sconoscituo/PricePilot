from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """회원가입 요청 스키마"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """사용자 응답 스키마"""
    id: int
    email: str
    is_active: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT 토큰 응답 스키마"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """토큰 내부 데이터"""
    email: str | None = None
