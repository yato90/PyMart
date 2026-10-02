import pytest


@pytest.mark.asyncio
async def test_create_and_get_category(client):
    response = await client.post(
        "/categories",
        json={"name": "Electronics"},
    )

    assert response.status_code == 200

    category = response.json()

    assert category["name"] == "Electronics"
    assert "id" in category

    category_id = category["id"]

    response = await client.get(
        f"/categories/{category_id}",
    )

    assert response.status_code == 200
    assert response.json() == category