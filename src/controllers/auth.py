import json
from typing import Annotated

from src.schemas.auth import LoginIn
from src.security import sign_jwt
from src.views.auth import LoginOut
from fastapi import APIRouter, Header, HTTPException, Query, Request, status

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_token(user_id: int) -> LoginOut:
    return LoginOut(**sign_jwt(user_id=user_id))


@router.post("/login", response_model=LoginOut)
async def login_post(
    request: Request,
    user_id: Annotated[
        int | None,
        Query(
            description=(
                "Se preenchido, o Body pode ficar vazio. No Insomnia: aba **Query** → user_id = 1"
            ),
        ),
    ] = None,
    x_user_id: Annotated[
        int | None,
        Header(
            alias="X-User-Id",
            description="Alternativa ao Body: header X-User-Id = 1",
        ),
    ] = None,
) -> LoginOut:
    """Ordem: Query -> Header -> JSON -> Form."""
    if user_id is not None:
        return _issue_token(user_id)
    if x_user_id is not None:
        return _issue_token(x_user_id)

    content_type = (request.headers.get("content-type") or "").lower()
    if (
        "application/x-www-form-urlencoded" in content_type
        or "multipart/form-data" in content_type
    ):
        form = await request.form()
        raw_user_id = form.get("user_id")
        if raw_user_id is not None:
            try:
                return _issue_token(int(raw_user_id))
            except (TypeError, ValueError) as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="No formulário, user_id deve ser inteiro",
                ) from exc

    raw_body = await request.body()
    if raw_body:
        try:
            parsed = json.loads(raw_body.decode("utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            parsed = None

        if isinstance(parsed, dict):
            try:
                data = LoginIn.model_validate(parsed)
                return _issue_token(data.user_id)
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail='No JSON, envie {"user_id": <inteiro>}',
                ) from exc

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail={
            "message": "Informe user_id de um destes jeitos (o Insomnia costuma não enviar Body no POST):",
            "opcoes": [
                "Query: na URL ou na aba Query / Params → user_id = 1",
                "Header: X-User-Id = 1",
                'Body JSON: {"user_id": 1} (Body → tipo JSON, sem template vazio)',
            ],
        },
    )
