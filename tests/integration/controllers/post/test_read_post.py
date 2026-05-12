import pytest_asyncio
from fastapi import status
from httpx import AsyncClient


@pytest_asyncio.fixture(autouse=True)
async def populate_db(db):
    from src.schemas.post import PostIn
    from src.services.post import PostService

    service = PostService()
    await service.create(PostIn(title="post 1", content="some content", published=True))
    await service.create(PostIn(title="post 2", content="some content", published=True))
    await service.create(
        PostIn(title="post 3", content="some content", published=False)
    )


async def test_read_post_success(client: AsyncClient, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    post_id = 1
    response = await client.get(f"/posts/{post_id}", headers=headers)

    content = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert content["id"] == post_id


async def test_read_post_not_authenticated_fail(client: AsyncClient):

    post_id = 1
    response = await client.get(f"/posts/{post_id}", headers={})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_read_post_not_found_fail(client: AsyncClient, access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    post_id = 4
    response = await client.get(f"/posts/{post_id}", headers=headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
