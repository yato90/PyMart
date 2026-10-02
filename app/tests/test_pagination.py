import pytest


@pytest.mark.asyncio
async def test_category_products_pagination(client):
    # Создаём категорию
    response = await client.post(
        "/categories",
        json={"name": "Pagination"},
    )

    assert response.status_code == 200

    category_id = response.json()["id"]

    # Создаём 5 продуктов
    for i in range(5):
        response = await client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": "10.00",
                "category_id": category_id,
            },
        )

        assert response.status_code == 200

    # Первая страница
    response = await client.get(
        f"/categories/{category_id}/products",
        params={"limit": 2},
    )

    assert response.status_code == 200

    first_page = response.json()

    assert len(first_page["items"]) == 2
    assert first_page["next_cursor"] is not None

    # Вторая страница
    response = await client.get(
        f"/categories/{category_id}/products",
        params={
            "limit": 2,
            "cursor": first_page["next_cursor"],
        },
    )

    assert response.status_code == 200

    second_page = response.json()

    assert len(second_page["items"]) == 2
    assert second_page["next_cursor"] is not None

    # Проверяем, что продукты не повторяются
    first_ids = {
        product["id"]
        for product in first_page["items"]
    }

    second_ids = {
        product["id"]
        for product in second_page["items"]
    }

    assert first_ids.isdisjoint(second_ids)

@pytest.mark.asyncio
async def test_category_products_last_page(client):
    response = await client.post(
        "/categories",
        json={"name": "Last Page"},
    )

    assert response.status_code == 200

    category_id = response.json()["id"]

    for i in range(3):
        response = await client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": "10.00",
                "category_id": category_id,
            },
        )

        assert response.status_code == 200

    # Первая страница
    response = await client.get(
        f"/categories/{category_id}/products",
        params={"limit": 2},
    )

    assert response.status_code == 200

    first_page = response.json()

    assert len(first_page["items"]) == 2
    assert first_page["next_cursor"] is not None

    # Последняя страница
    response = await client.get(
        f"/categories/{category_id}/products",
        params={
            "limit": 2,
            "cursor": first_page["next_cursor"],
        },
    )

    assert response.status_code == 200

    last_page = response.json()

    assert len(last_page["items"]) == 1
    assert last_page["next_cursor"] is None

@pytest.mark.asyncio
async def test_category_products_invalid_cursor(client):
    response = await client.post(
        "/categories",
        json={"name": "Invalid Cursor"},
    )

    assert response.status_code == 200

    category_id = response.json()["id"]

    response = await client.get(
        f"/categories/{category_id}/products",
        params={
            "limit": 2,
            "cursor": "not-a-valid-cursor",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid cursor"

@pytest.mark.asyncio
async def test_products_pagination(client):
    # Создаём категорию
    response = await client.post(
        "/categories",
        json={"name": "Global Pagination"},
    )

    assert response.status_code == 200

    category_id = response.json()["id"]

    # Создаём 5 товаров
    for i in range(5):
        response = await client.post(
            "/products",
            json={
                "name": f"Global Product {i}",
                "price": "10.00",
                "category_id": category_id,
            },
        )

        assert response.status_code == 200

    # Первая страница
    response = await client.get(
        "/products",
        params={"limit": 2},
    )

    assert response.status_code == 200

    first_page = response.json()

    assert len(first_page["items"]) == 2
    assert first_page["next_cursor"] is not None

    # Вторая страница
    response = await client.get(
        "/products",
        params={
            "limit": 2,
            "cursor": first_page["next_cursor"],
        },
    )

    assert response.status_code == 200

    second_page = response.json()

    assert len(second_page["items"]) == 2
    assert second_page["next_cursor"] is not None

    # Страницы не должны пересекаться
    first_ids = {
        product["id"]
        for product in first_page["items"]
    }

    second_ids = {
        product["id"]
        for product in second_page["items"]
    }

    assert first_ids.isdisjoint(second_ids)