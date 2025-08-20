import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, ConfigDict
from typing import List
import httpx

current_dir = Path(__file__).parent
stage2_path = current_dir.parent / "Stage2"
sys.path.insert(0, str(stage2_path))

try:
    from librarys2 import Library
    print(f"Library module successfully imported: {stage2_path}/librarys2.py")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python paths: {sys.path}")
    raise

app = FastAPI(
    title="Library Management API",
    description="API for managing books with Open Library integration",
    version="2.0.0"
)

JSON_FILE = os.path.abspath(os.path.join(current_dir, "library_data.json"))
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        f.write("[]")
print(f"🛠️ Library file path: {JSON_FILE}")
lib = Library(JSON_FILE)

class BookModel(BaseModel):
    title: str
    authors: List[str]
    isbn: str
    available: bool

    model_config = ConfigDict(from_attributes=True)

class ISBNModel(BaseModel):
    isbn: str

class BookCreateModel(BaseModel):
    title: str
    authors: List[str]
    isbn: str

class BorrowReturnModel(BaseModel):
    isbn: str

@app.post("/books/isbn", response_model=BookModel, status_code=status.HTTP_201_CREATED)
def add_book_by_isbn(isbn_data: ISBNModel):
    result = lib.add_book_by_isbn(isbn_data.isbn)
    if "Error" in result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=result)
    return lib.books[isbn_data.isbn]

@app.post("/books", response_model=BookModel, status_code=status.HTTP_201_CREATED)
def add_book_manual(book: BookCreateModel):
    result = lib.add_book(book.title, book.authors, book.isbn)
    if "Error" in result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=result)
    return lib.books[book.isbn]

@app.get("/books", response_model=List[BookModel])
def list_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page")
):
    books_list = list(lib.books.values())
    return books_list[skip:skip + limit]

@app.get("/books/search", response_model=List[BookModel])
def search_books(
    query: str = Query(..., min_length=2, description="Search term"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results")
):
    results = [
        book for book in lib.books.values()
        if query.lower() in book.title.lower() or 
        any(query.lower() in author.lower() for author in book.authors)
    ]
    return results[:limit]

@app.get("/books/{isbn}", response_model=BookModel)
def get_book(isbn: str):
    book = lib.find_book(isbn)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ISBN: {isbn} not found"
        )
    return book

@app.delete("/books/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(isbn: str):
    result = lib.remove_book(isbn)
    if "Error" in result:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=result)

@app.put("/books/{isbn}/borrow", response_model=BookModel)
def borrow_book(isbn: str):
    result = lib.borrow_book(isbn)
    if "Error" in result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=result)
    return lib.books[isbn]

@app.put("/books/{isbn}/return", response_model=BookModel)
def return_book(isbn: str):
    result = lib.return_book(isbn)
    if "Error" in result:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=result)
    return lib.books[isbn]

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "total_books": len(lib.books),
        "data_file": JSON_FILE,
        "file_exists": os.path.exists(JSON_FILE)
    }

@app.get("/stats")
def get_stats():
    total_books = len(lib.books)
    available_books = sum(1 for book in lib.books.values() if book.available)
    borrowed_books = total_books - available_books
    return {
        "total_books": total_books,
        "available_books": available_books,
        "borrowed_books": borrowed_books
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting API... http://localhost:8000")
    print(f"JSON file path: {JSON_FILE}")
    print(f"Initial book count: {len(lib.books)}")
    print(f"File exists?: {os.path.exists(JSON_FILE)}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")