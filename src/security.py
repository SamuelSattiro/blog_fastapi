import time
from typing import Annotated, Any
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, field_validator

SECRET = "preciso-ser-muito-longo-para-testar-o-limite-de-caracteres-do-jwt"
ALGORITHM = "HS256"
ISSUER = "curso-fastapi.com.br"
AUDIENCE = "curso-fastapi"


class AccessToken(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    nbf: int
    jti: str

    @field_validator("exp", "iat", "nbf", mode="before")
    @classmethod
    def time_claims_to_int(cls, v: Any) -> int:
        return int(v)


class JWTToken(BaseModel):
    access_token: AccessToken


def sign_jwt(user_id: int) -> dict[str, str]:
    now = int(time.time())
    payload = {
        "iss": ISSUER,
        "sub": str(user_id),
        "aud": AUDIENCE,
        "exp": now + (60 * 30),
        "iat": now,
        "nbf": now,
        "jti": uuid4().hex,
    }
    raw = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    token_str = raw if isinstance(raw, str) else raw.decode("utf-8")
    return {"access_token": token_str, "token_type": "bearer"}


async def decode_jwt(token: str) -> JWTToken | None:
    try:
        decoded_token = jwt.decode(
            token,
            SECRET,
            algorithms=[ALGORITHM],
            audience=AUDIENCE,
            issuer=ISSUER,
        )
        _token = JWTToken.model_validate({"access_token": decoded_token})
        return _token if _token.access_token.exp >= int(time.time()) else None
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JWTToken:
        authorization = request.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")

        if credentials:
            if not scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                )
            payload = await decode_jwt(credentials)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                )
            return payload
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code",
            )


async def get_current_user(
    token: Annotated[JWTToken, Depends(JWTBearer())],
) -> dict[str, int]:
    return {"user_id": int(token.access_token.sub)}


async def login_required(
    current_user: Annotated[dict[str, int], Depends(get_current_user)],
) -> dict[str, int]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied"
        )
    return current_user
