import json
import os
from typing import List, Dict, Optional

class Book:
    def __init__(self, title: str, authors: List[str], isbn: str):
        self.title = title
        self.authors = authors
        self.isbn = isbn
        self.available = True

    def __str__(self):
        status = "Available" if self.available else "Borrowed"
        return f"{self.title} by {', '.join(self.authors)} (ISBN: {self.isbn}) - {status}"

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'authors': self.authors,
            'isbn': self.isbn,
            'available': self.available
        }

class Library:
    def __init__(self, filename: str = "library.json"):
        self.filename = os.path.abspath(filename)
        self.books: Dict[str, Book] = {}
        self._ensure_directory()
        self._load_books()

    def add_book(self, title: str, authors: List[str], isbn: str) -> str:
        if not all([title, isbn, authors]):
            return "Error: Title, authors and ISBN are required!"
        
        if isbn in self.books:
            return f"Error: ISBN {isbn} already exists!"
            
        self.books[isbn] = Book(title, authors, isbn)
        self._save_books()
        return f"Added: {title}"

    def borrow_book(self, isbn: str) -> str:
            if isbn not in self.books:
                return "Error: Book not found!"
            
            if not self.books[isbn].available:
                return "Error: Book already borrowed!"
            
            self.books[isbn].available = False
            self._save_books()
            return f"Borrowed: {self.books[isbn].title}"

    def return_book(self, isbn: str) -> str:
        if isbn not in self.books:
            return "Error: Book not found!"
            
        if self.books[isbn].available:
            return "Error: Book wasn't borrowed!"
            
        self.books[isbn].available = True
        self._save_books()
        return f"Returned: {self.books[isbn].title}"

    def remove_book(self, isbn: str) -> str:
        if isbn in self.books:
            title = self.books[isbn].title
            del self.books[isbn]
            self._save_books()
            return f"Removed: {title}"
        return "Error: Book not found!"

    def find_book(self, isbn: str) -> Optional[Book]:
        return self.books.get(isbn)

    def list_books(self) -> List[str]:
        if not self.books:
            return ["No books in library"]
        return [str(book) for book in self.books.values()]

    def _ensure_directory(self):
        dir_path = os.path.dirname(self.filename)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

    def _load_books(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    books_data = json.load(f)
                    self.books = {
                        book['isbn']: Book(
                            title=book['title'],
                            authors=book['authors'],
                            isbn=book['isbn']
                        )
                        for book in books_data
                    }
                    for isbn, book_data in zip(self.books.keys(), books_data):
                        self.books[isbn].available = book_data.get('available', True)
            except (json.JSONDecodeError, KeyError):
                self.books = {}

    def _save_books(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(
                    [book.to_dict() for book in self.books.values()],
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except (IOError, TypeError) as e:
            raise RuntimeError(f"Failed to save library: {str(e)}")