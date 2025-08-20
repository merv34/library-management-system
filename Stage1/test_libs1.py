import pytest
from librarys1 import Book, Library
import os
import json
import tempfile

def create_temp_library_file(data=None):
    if data is None:
        data = []
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, "test_library.json")
    with open(temp_file, 'w') as f:
        json.dump(data, f)
    return temp_file

class TestBook:
    def test_book_creation(self):
        book = Book("Test Book", ["Author 1", "Author 2"], "1234567890")
        assert book.title == "Test Book"
        assert book.authors == ["Author 1", "Author 2"]
        assert book.isbn == "1234567890"
        assert book.available is True

    def test_book_str_representation(self):
        book = Book("Test Book", ["Author 1"], "1234567890")
        assert "Test Book by Author 1 (ISBN: 1234567890) - Available" in str(book)
        
        book.available = False
        assert "Borrowed" in str(book)

    def test_to_dict_method(self):
        book = Book("Test Book", ["Author 1"], "1234567890")
        book_dict = book.to_dict()
        assert book_dict == {
            'title': 'Test Book',
            'authors': ['Author 1'],
            'isbn': '1234567890',
            'available': True
        }

class TestLibrary:
    def test_library_init_with_empty_file(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        assert len(lib.books) == 0
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_library_init_with_existing_data(self):
        test_data = [
            {
                'title': 'Existing Book',
                'authors': ['Existing Author'],
                'isbn': '1111111111',
                'available': True
            }
        ]
        temp_file = create_temp_library_file(test_data)
        lib = Library(temp_file)
        assert len(lib.books) == 1
        assert '1111111111' in lib.books
        assert lib.books['1111111111'].title == 'Existing Book'
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_add_book_success(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        result = lib.add_book("New Book", ["New Author"], "1234567890")
        assert "Added: New Book" in result
        assert len(lib.books) == 1
        assert "1234567890" in lib.books
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_add_book_missing_fields(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        result = lib.add_book("", ["Author"], "123")
        assert "Error: Title, authors and ISBN are required!" in result
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_add_duplicate_isbn(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        lib.add_book("Book 1", ["Author 1"], "123")
        result = lib.add_book("Book 2", ["Author 2"], "123")
        assert "Error: ISBN 123 already exists!" in result
        assert len(lib.books) == 1
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_remove_book_success(self):
        test_data = [
            {
                'title': 'Book to Remove',
                'authors': ['Author'],
                'isbn': '123',
                'available': True
            }
        ]
        temp_file = create_temp_library_file(test_data)
        lib = Library(temp_file)
        result = lib.remove_book("123")
        assert "Removed: Book to Remove" in result
        assert len(lib.books) == 0
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_remove_nonexistent_book(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        result = lib.remove_book("999")
        assert "Error: Book not found!" in result
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_borrow_book_success(self):
        test_data = [
            {
                'title': 'Available Book',
                'authors': ['Author'],
                'isbn': '123',
                'available': True
            }
        ]
        temp_file = create_temp_library_file(test_data)
        lib = Library(temp_file)
        result = lib.borrow_book("123")
        assert "Borrowed: Available Book" in result
        assert lib.books["123"].available is False
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_borrow_nonexistent_book(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        result = lib.borrow_book("999")
        assert "Error: Book not found!" in result
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_borrow_already_borrowed_book(self):
        test_data = [
            {
                'title': 'Borrowed Book',
                'authors': ['Author'],
                'isbn': '123',
                'available': False
            }
        ]
        temp_file = create_temp_library_file(test_data)
        lib = Library(temp_file)
        result = lib.borrow_book("123")
        assert "Error: Book already borrowed!" in result
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_return_book_success(self):
        test_data = [
            {
                'title': 'Borrowed Book',
                'authors': ['Author'],
                'isbn': '123',
                'available': False
            }
        ]
        temp_file = create_temp_library_file(test_data)
        lib = Library(temp_file)
        result = lib.return_book("123")
        assert "Returned: Borrowed Book" in result
        assert lib.books["123"].available is True
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_return_nonexistent_book(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        result = lib.return_book("999")
        assert "Error: Book not found!" in result
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_return_already_available_book(self):
        test_data = [
            {
                'title': 'Available Book',
                'authors': ['Author'],
                'isbn': '123',
                'available': True
            }
        ]
        temp_file = create_temp_library_file(test_data)
        lib = Library(temp_file)
        result = lib.return_book("123")
        assert "Error: Book wasn't borrowed!" in result
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_find_book_success(self):
        test_data = [
            {
                'title': 'Found Book',
                'authors': ['Author'],
                'isbn': '123',
                'available': True
            }
        ]
        temp_file = create_temp_library_file(test_data)
        lib = Library(temp_file)
        book = lib.find_book("123")
        assert book is not None
        assert book.title == "Found Book"
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_find_nonexistent_book(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        book = lib.find_book("999")
        assert book is None
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_list_books_empty(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        result = lib.list_books()
        assert result == ["No books in library"]
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_list_books_with_items(self):
        test_data = [
            {
                'title': 'Book 1',
                'authors': ['Author 1'],
                'isbn': '111',
                'available': True
            },
            {
                'title': 'Book 2',
                'authors': ['Author 2'],
                'isbn': '222',
                'available': False
            }
        ]
        temp_file = create_temp_library_file(test_data)
        lib = Library(temp_file)
        result = lib.list_books()
        assert len(result) == 2
        assert "Book 1 by Author 1 (ISBN: 111) - Available" in result
        assert "Book 2 by Author 2 (ISBN: 222) - Borrowed" in result
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))

    def test_save_books_on_operations(self):
        temp_file = create_temp_library_file()
        lib = Library(temp_file)
        
        lib.add_book("Test Save", ["Author"], "123")
        with open(temp_file, 'r') as f:
            saved_data = json.load(f)
        assert len(saved_data) == 1
        assert saved_data[0]['title'] == "Test Save"
        
        lib.borrow_book("123")
        with open(temp_file, 'r') as f:
            saved_data = json.load(f)
        assert saved_data[0]['available'] is False
        
        os.remove(temp_file)
        os.rmdir(os.path.dirname(temp_file))