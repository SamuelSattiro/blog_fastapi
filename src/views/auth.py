from pydantic import BaseModel, Field


class LoginOut(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer", description="Esquema HTTP (RFC 6750)")
