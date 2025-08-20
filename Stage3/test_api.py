import pytest
from fastapi.testclient import TestClient
from api import app, JSON_FILE
import json
import os

client = TestClient(app)

TEST_BOOK = {
    "title": "Test Kitap",
    "authors": ["Test Yazar"],
    "isbn": "1234567890"
}
TEST_ISBN = "9789753425426" 

@pytest.fixture(autouse=True)
def cleanup():
    yield
    if os.path.exists(JSON_FILE):
        os.remove(JSON_FILE)

def test_list_books():
    response = client.get("/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_book_manual():
    response = client.post("/books", json=TEST_BOOK)
    assert response.status_code == 201
    assert response.json()["title"] == TEST_BOOK["title"]

def test_add_book_by_isbn():
    response = client.post("/books/isbn", json={"isbn": TEST_ISBN})
    assert response.status_code in (201, 422, 400)  
    if response.status_code == 201:
        assert "title" in response.json()

def test_get_book():
    client.post("/books", json=TEST_BOOK)
    
    response = client.get(f"/books/{TEST_BOOK['isbn']}")
    assert response.status_code == 200
    assert response.json()["isbn"] == TEST_BOOK["isbn"]

def test_delete_book():
    client.post("/books", json=TEST_BOOK)
    
    response = client.delete(f"/books/{TEST_BOOK['isbn']}")
    assert response.status_code == 204
    
    response = client.get(f"/books/{TEST_BOOK['isbn']}")
    assert response.status_code == 404

def test_borrow_return_flow():
    client.post("/books", json=TEST_BOOK)
    
    response = client.put(f"/books/{TEST_BOOK['isbn']}/borrow")
    assert response.status_code == 200
    assert response.json()["available"] is False
    
    response = client.put(f"/books/{TEST_BOOK['isbn']}/return")
    assert response.status_code == 200
    assert response.json()["available"] is True

def test_search_books():
    client.post("/books", json=TEST_BOOK)
    
    response = client.get("/books/search", params={"query": "test"})
    assert response.status_code == 200
    assert len(response.json()) > 0