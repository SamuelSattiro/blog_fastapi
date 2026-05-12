from pydantic import BaseModel, ConfigDict, Field


class LoginIn(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"user_id": 1}]},
    )

    user_id: int = Field(description="Identificador do usuário para emitir o JWT")
