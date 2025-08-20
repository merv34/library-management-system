import pytest
import json
import os
import httpx
from unittest.mock import patch, MagicMock
import sys
from typing import List

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from librarys2 import Library, Book

@pytest.fixture
def temp_library(tmp_path):
    lib_file = tmp_path / "test_library.json"
    yield Library(filename=str(lib_file))
    if os.path.exists(lib_file):
        os.remove(lib_file)

@pytest.fixture
def sample_book():
    return {
        "title": "Test Book",
        "authors": ["Author One", "Author Two"],
        "isbn": "1234567890"
    }

def create_mock_request():
    mock_request = MagicMock(spec=httpx.Request)
    mock_request.method = "GET"
    mock_request.url = "https://example.com"
    return mock_request

def create_mock_response(status_code=200):
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = status_code
    mock_response.request = create_mock_request()
    return mock_response

def test_book_initialization(sample_book):
    book = Book(**sample_book)
    assert book.title == sample_book["title"]
    assert book.authors == sample_book["authors"]
    assert book.isbn == sample_book["isbn"]
    assert book.available == True

def test_book_str_representation(sample_book):
    book = Book(**sample_book)
    assert sample_book["title"] in str(book)
    assert "Author One" in str(book)
    assert sample_book["isbn"] in str(book)
    assert "Available" in str(book)

def test_book_to_dict(sample_book):
    book = Book(**sample_book)
    book_dict = book.to_dict()
    assert book_dict["title"] == sample_book["title"]
    assert book_dict["authors"] == sample_book["authors"]
    assert book_dict["isbn"] == sample_book["isbn"]
    assert book_dict["available"] == True

def test_library_init(temp_library):
    assert isinstance(temp_library.books, dict)
    assert len(temp_library.books) == 0

def test_add_book_manual(temp_library, sample_book):
    result = temp_library.add_book(**sample_book)
    assert "Added" in result
    assert sample_book["title"] in result
    assert len(temp_library.books) == 1
    assert sample_book["isbn"] in temp_library.books

def test_add_book_missing_fields(temp_library):
    result = temp_library.add_book("", [], "")
    assert "Error" in result
    assert len(temp_library.books) == 0

def test_add_duplicate_book(temp_library, sample_book):
    temp_library.add_book(**sample_book)
    result = temp_library.add_book(**sample_book)
    assert "Error" in result
    assert "already exists" in result

def test_remove_book(temp_library, sample_book):
    temp_library.add_book(**sample_book)
    result = temp_library.remove_book(sample_book["isbn"])
    assert "Removed" in result
    assert len(temp_library.books) == 0

def test_remove_nonexistent_book(temp_library):
    result = temp_library.remove_book("nonexistent")
    assert "Error" in result

def test_borrow_return_book(temp_library, sample_book):
    temp_library.add_book(**sample_book)
    
    borrow_result = temp_library.borrow_book(sample_book["isbn"])
    assert "Borrowed" in borrow_result
    assert not temp_library.books[sample_book["isbn"]].available
    
    return_result = temp_library.return_book(sample_book["isbn"])
    assert "Returned" in return_result
    assert temp_library.books[sample_book["isbn"]].available

def test_borrow_already_borrowed(temp_library, sample_book):
    temp_library.add_book(**sample_book)
    temp_library.borrow_book(sample_book["isbn"])
    result = temp_library.borrow_book(sample_book["isbn"])
    assert "Error" in result
    assert "already borrowed" in result

def test_return_not_borrowed(temp_library, sample_book):
    temp_library.add_book(**sample_book)
    result = temp_library.return_book(sample_book["isbn"])
    assert "Error" in result
    assert "wasn't borrowed" in result

def test_find_book(temp_library, sample_book):
    temp_library.add_book(**sample_book)
    book = temp_library.find_book(sample_book["isbn"])
    assert book is not None
    assert book.title == sample_book["title"]

def test_find_nonexistent_book(temp_library):
    book = temp_library.find_book("nonexistent")
    assert book is None

def test_list_books(temp_library, sample_book):
    assert "No books" in temp_library.list_books()[0]
    temp_library.add_book(**sample_book)
    books_list = temp_library.list_books()
    assert len(books_list) == 1
    assert sample_book["title"] in books_list[0]

@patch('librarys2.httpx.get')
def test_add_book_by_isbn_success(mock_get, temp_library):
    
    mock_book_response = create_mock_response()
    mock_book_response.json.return_value = {
        "title": "API Book",
        "authors": [{"key": "/authors/OL1A"}],
        "publishers": ["Test Publisher"]
    }
    
    mock_author_response = create_mock_response()
    mock_author_response.json.return_value = {"name": "API Author"}
    
    mock_get.side_effect = [mock_book_response, mock_author_response]
    
    result = temp_library.add_book_by_isbn("9876543210")
    assert "Added" in result
    assert "API Book" in result
    assert len(temp_library.books) == 1
    assert "9876543210" in temp_library.books
    assert temp_library.books["9876543210"].authors == ["API Author"]

@patch('librarys2.httpx.get')
def test_add_book_by_isbn_missing_authors(mock_get, temp_library):
    mock_response = create_mock_response()
    mock_response.json.return_value = {
        "title": "No Author Book",
        "publishers": ["Test Publisher"]
    }
    mock_get.return_value = mock_response
    
    result = temp_library.add_book_by_isbn("9876543210")
    assert "Added" in result
    assert temp_library.books["9876543210"].authors == ["Unknown Author"]

@patch('librarys2.httpx.get')
def test_add_book_by_isbn_api_failure(mock_get, temp_library):
    mock_get.side_effect = httpx.RequestError("API Error", request=create_mock_request())
    
    result = temp_library.add_book_by_isbn("9876543210")
    assert "Error" in result
    assert "API" in result or "not found" in result
    assert len(temp_library.books) == 0

@patch('librarys2.httpx.get')
def test_add_book_by_isbn_http_error(mock_get, temp_library):
    mock_response = create_mock_response(404)
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found", 
        request=create_mock_request(),
        response=mock_response
    )
    mock_get.return_value = mock_response
    
    result = temp_library.add_book_by_isbn("9876543210")
    assert "Error" in result
    assert "404" in result
    assert len(temp_library.books) == 0

def test_add_book_by_isbn_empty_input(temp_library):
    result = temp_library.add_book_by_isbn("")
    assert "Error" in result
    assert "ISBN is required" in result

def test_library_persistence(tmp_path, sample_book):
    lib_file = tmp_path / "persistence_test.json"
    lib = Library(filename=str(lib_file))
    
    lib.add_book(
        title=sample_book["title"],
        authors=sample_book["authors"],
        isbn=sample_book["isbn"]
    )
    assert len(lib.books) == 1
    
    lib2 = Library(filename=str(lib_file))
    assert len(lib2.books) == 1
    assert sample_book["isbn"] in lib2.books
    assert lib2.books[sample_book["isbn"]].title == sample_book["title"]