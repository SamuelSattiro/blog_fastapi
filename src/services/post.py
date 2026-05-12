from databases.interfaces import Record
from src.database import database
from src.models.post import posts
from src.schemas.post import PostIn, PostUpdateIn
from fastapi import HTTPException


class PostService:
    async def read_all(
        self, published: bool, limit: int, skip: int = 0
    ) -> list[Record]:
        query = (
            posts.select()
            .limit(limit)
            .offset(skip)
            .where(posts.c.published == published)
        )
        return await database.fetch_all(query)

    async def create(self, post: PostIn) -> int:
        command = posts.insert().values(
            title=post.title,
            content=post.content,
            published_at=post.published_at,
            published=post.published,
        )
        return await database.execute(command)

    async def read(self, id: int) -> Record:
        return await self.__get_by_id(id)

    async def update(self, id: int, post: PostUpdateIn) -> Record:
        total = await self.count(id)
        if not total:
            raise HTTPException(status_code=404, detail="Post not found")

        data = post.model_dump(exclude_unset=True)
        command = posts.update().where(posts.c.id == id).values(**data)
        await database.execute(command)
        return await self.__get_by_id(id)

    async def delete(self, id: int) -> None:
        command = posts.delete().where(posts.c.id == id)
        await database.execute(command)

    async def count(self, id: int) -> int:
        query = "SELECT COUNT(id) as total FROM posts WHERE id = :id"
        result = await database.fetch_one(query, {"id": id})
        return result.total

    async def __get_by_id(self, id: int) -> Record:
        query = posts.select().where(posts.c.id == id)
        post = await database.fetch_one(query)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post
