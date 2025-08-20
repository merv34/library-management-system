import json
import os
import httpx
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

    def add_book_by_isbn(self, isbn: str) -> str:
        try:
            if not isbn:
                return "Error: ISBN is required!"
                
            book_data = self._fetch_book_data(isbn)
            if not book_data:
                return "Error: Book not found via API!"
                
            return self.add_book(
                title=book_data.get('title', 'Unknown Title'),
                authors=book_data.get('authors', ['Unknown Author']),
                isbn=isbn
            )
        except Exception as e:
            return f"API Error: {str(e)}"

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

    def _fetch_book_data(self, isbn: str) -> Optional[Dict]:
        try:
            response = httpx.get(
                f"https://openlibrary.org/isbn/{isbn}.json",
                timeout=10.0,
                follow_redirects=True
            )
            response.raise_for_status()
            data = response.json()

            if 'authors' in data:
                authors = []
                for author in data['authors']:
                    author_name = self._fetch_author_name(author['key'])
                    authors.append(author_name if author_name else 'Unknown Author')
                data['authors'] = authors

            return data
        except (httpx.RequestError, json.JSONDecodeError):
            return None

    def _fetch_author_name(self, author_key: str) -> Optional[str]:
        try:
            response = httpx.get(
                f"https://openlibrary.org{author_key}.json",
                timeout=5.0
            )
            return response.json().get('name')
        except (httpx.RequestError, json.JSONDecodeError):
            return None
    
    def _save_books(self):
        try:
            print(f"💾 Kaydediliyor: {self.filename}")  # Debug
            with open(self.filename, 'w', encoding='utf-8') as f:
                data = [book.to_dict() for book in self.books.values()]
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✅ {len(data)} kitap başarıyla kaydedildi")
            print("Gerçekten dosya var mı?:", os.path.exists(self.filename))
            print("Gerçek dosya yolu:", os.path.abspath(self.filename))
        except Exception as e:
            print(f"Kayıt hatası: {str(e)}")
            raise RuntimeError(f"Dosya yazılamadı: {self.filename}")

    def _load_books(self):
        if os.path.exists(self.filename):
            print(f"📖 Yükleniyor: {self.filename}")  # Debug
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
                print(f"🔍 {len(self.books)} kitap yüklendi")
            except Exception as e:
                print(f"⚠ Yükleme hatası: {str(e)}")
                self.books = {}
        else:
            print("ℹ Dosya bulunamadı, yeni kütüphane oluşturuluyor")
            self.books = {}