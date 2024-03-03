import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books, sellers

# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "lmblf", "last_name": "vlsl", "email": "bvdmvlfl@gmail.com", "password": "0000"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "first_name": "lmblf",
        "last_name": "vlsl",
        "email": "bvdmvlfl@gmail.ru",
        "id": result_data["id"]
    }

# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller_1 = sellers.Seller(
        first_name="lblb", last_name="swl", email="swl@gmail.com", password="vmbmk"
    )
    seller_2 = sellers.Seller(
        first_name="vfkee", last_name="flv", email="flv@mail.ru", password="777"
    )

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    result_data = response.json()

    assert result_data == {
        "sellers": [
            {
                'first_name': 'lblb',
                'last_name': 'swl', 
                'email': 'swl@gmail.com',
                'id': seller_1.id
            },

            {
                'first_name': 'vfkee',
                'last_name': 'flv',
                'email': 'flv@mail.ru',
                'id': seller_2.id,
            }
        ]
    }


# Тест на ручку получения одного продавца
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    # Создаем продавцов вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name='lmblf', last_name='vlsl', email='bvdmvlfl@gmail.com', password='0000')

    db_session.add_all([seller])
    await db_session.flush()

    book = books.Book(author='bmll', title='dfmv', year=2000, count_pages=100, seller_id=seller.id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    result_data = response.json()

    assert result_data == {
        'first_name': 'lmblf', 
        'last_name': 'vlsl',
        'email': 'bvdmvlfl@gmail.com',
        "books": [
                    {
                        'author': 'bmll',
                        'title': 'dfmv', 
                        'year': 2000,
                        'count_pages': 100,
                        'id': book.id,
                        'seller_id': seller.id
                    }

        ]
    }


# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name='lmblf', last_name='vlsl', email='bvdmvlfl@gmail.com', password='0000')

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления данных о продавце
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем продавца вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    seller = sellers.Seller(first_name='lmblf', last_name='vlsl', email='bvdmvlfl@gmail.com', password='0000')

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/sellers/{seller.id}",
        json={'id': seller.id, 'first_name': 'lef', 'last_name': 'slpvps', 'email': 'slpvps@gmail.com'})

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller.id)
    assert res.id == seller.id
    assert res.first_name == 'lef'
    assert res.last_name == 'slpvps'
    assert res.email == 'slpvps@gmail.com'