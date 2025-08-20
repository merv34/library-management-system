# Library Management System 🏛️📚

A comprehensive 3-stage library management system featuring terminal interface, Open Library API integration, and FastAPI web service.

## 📋 Project Overview

This project implements a complete library management system across three stages:
- **Stage 1**: Terminal-based OOP application with JSON persistence
- **Stage 2**: Open Library API integration for ISBN-based book addition
- **Stage 3**: FastAPI web service with RESTful endpoints

## 🚀 Features

### Stage 1 - Core Library System
- Object-oriented design with Book and Library classes
- JSON data persistence
- Full CRUD operations (Add, Remove, List, Search)
- Borrow/return functionality
- Comprehensive unit testing

### Stage 2 - API Integration
- Open Library API integration
- ISBN-based book lookup and automatic data retrieval
- Advanced error handling and network resilience
- Enhanced testing with HTTP mocking

### Stage 3 - FastAPI Service
- FastAPI web service with automatic Swagger documentation
- RESTful endpoints with proper HTTP status codes
- Search functionality with pagination
- Health check and statistics endpoints
- Comprehensive API testing

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/library-management-system.git
cd library-management-system
```

### 2. Virtual Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Stage 1 - Terminal Application
```bash
cd Stage1
python mains1.py
```

**Menu Options:**
1. Add Book (Manual Entry)
2. Remove Book
3. List All Books
4. Search Book
5. Borrow Book
6. Return Book
7. Exit

### Stage 2 - Enhanced Terminal Application
```bash
cd Stage2
python mains2.py
```

**Additional Feature:** Option 2 - "Add Book by ISBN (API)"

### Stage 3 - FastAPI Server
```bash
cd Stage3
uvicorn api:app --reload
```
Access API documentation at: http://localhost:8000/docs

## 📚 API Documentation (Stage 3)

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/books/isbn` | Add book by ISBN |
| `POST` | `/books` | Add book manually |
| `GET` | `/books` | List all books |
| `GET` | `/books/{isbn}` | Get book by ISBN |
| `DELETE` | `/books/{isbn}` | Delete book by ISBN |
| `PUT` | `/books/{isbn}/borrow` | Borrow a book |
| `PUT` | `/books/{isbn}/return` | Return a book |
| `GET` | `/books/search` | Search books |
| `GET` | `/health` | Health check |
| `GET` | `/stats` | Library statistics |

### Example API Requests

```bash
# Add book by ISBN
curl -X POST "http://localhost:8000/books/isbn" \
  -H "Content-Type: application/json" \
  -d '{"isbn": "9789753425426"}'

# Get all books
curl "http://localhost:8000/books"

# Search books
curl "http://localhost:8000/books/search?query=tolkien"
```

## 🧪 Testing

### Stage 1 Tests
```bash
cd Stage1
pytest test_libs1.py -v
```

### Stage 2 Tests
```bash
cd Stage2
pytest test_libs2.py -v
```

### Stage 3 Tests
```bash
cd Stage3
pytest test_api.py -v
```

## 📁 Project Structure

```
library-management-system/
├── Stage1/
│   ├── mains1.py
│   ├── librarys1.py
│   ├── test_libs1.py
│   ├── library_data.json
│   └── requirements.txt
├── Stage2/
│   ├── mains2.py
│   ├── librarys2.py
│   ├── test_libs2.py
│   ├── library_data.json
│   └── requirements.txt
├── Stage3/
│   ├── api.py
│   ├── test_api.py
│   └── requirements.txt
├── requirements.txt
├── .gitignore
└── README.md
```

## 🛠️ Technologies Used

- **Python 3.8+**
- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **HTTPX** - HTTP client
- **Pytest** - Testing framework
- **Uvicorn** - ASGI server

## 👥 Author

[Merve Güzel](https://github.com/merv34)


