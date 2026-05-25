from pydantic import AwareDatetime

from pydantic import BaseModel


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    published_at: AwareDatetime | None = None
