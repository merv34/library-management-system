import sys
import os
from typing import List

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from librarys2 import Library

def display_menu():
    print("\n==== LIBRARY MANAGEMENT SYSTEM ====")
    print("1. Add Book (Manual Entry)")
    print("2. Add Book by ISBN (API)")
    print("3. Remove Book")
    print("4. List All Books")
    print("5. Search Book")
    print("6. Borrow Book")
    print("7. Return Book")
    print("8. Exit")

def get_authors() -> List[str]:
    while True:
        authors = input("Enter authors (comma separated): ").strip()
        if authors:
            return [a.strip() for a in authors.split(',')]
        print("Error: At least one author is required!")

def get_input(prompt: str, required: bool = True) -> str:
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("Error: This field is required!")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    json_file = os.path.join(os.path.dirname(__file__), "library_data.json")
    lib = Library(json_file)
    
    while True:
        clear_screen()
        display_menu()
        choice = get_input("\nYour choice (1-8): ", required=True)
        
        try:
            if choice == '1':
                clear_screen()
                print("=== ADD NEW BOOK ===")
                title = get_input("Title: ", required=True)
                authors = get_authors()
                isbn = get_input("ISBN: ", required=True)
                print("\n" + lib.add_book(title, authors, isbn))
                
            elif choice == '2':
                clear_screen()
                print("=== ADD BOOK BY ISBN ===")
                isbn = get_input("Enter ISBN: ", required=True)
                print("\n" + lib.add_book_by_isbn(isbn))
                
            elif choice == '3':
                clear_screen()
                print("=== REMOVE BOOK ===")
                isbn = get_input("Enter ISBN to remove: ", required=True)
                print("\n" + lib.remove_book(isbn))
                
            elif choice == '4':
                clear_screen()
                print("=== ALL BOOKS ===")
                for book in lib.list_books():
                    print(book)
                
            elif choice == '5':
                clear_screen()
                print("=== SEARCH BOOK ===")
                isbn = get_input("Enter ISBN to search: ", required=True)
                book = lib.find_book(isbn)
                if book:
                    print(f"\n{book}")
                else:
                    print("\nBook not found")
                    
            elif choice == '6':
                clear_screen()
                print("=== BORROW BOOK ===")
                isbn = get_input("Enter ISBN to borrow: ", required=True)
                print("\n" + lib.borrow_book(isbn))
                
            elif choice == '7':
                clear_screen()
                print("=== RETURN BOOK ===")
                isbn = get_input("Enter ISBN to return: ", required=True)
                print("\n" + lib.return_book(isbn))
                
            elif choice == '8':
                print("\nThank you for using the Library System!")
                break
                
            else:
                print("\nInvalid choice! Please enter 1-8.")
            
            input("\nPress Enter to continue...")
            
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()