#!/usr/bin/env python3
"""Test script to understand Text-Fabric API"""

from tf.app import use

# Load dataset
A = use('etcbc/bhsa', silent=True)

print("Available attributes on A:")
print([attr for attr in dir(A) if not attr.startswith('_')])

# Test basic operations
print("\nTesting feature access...")
try:
    print("A.api:", hasattr(A, 'api'))
    print("A.F:", hasattr(A, 'F'))
    print("A.TF:", hasattr(A, 'TF'))

    # Try to access features through TF
    if hasattr(A, 'TF'):
        print("A.TF.F:", hasattr(A.TF, 'F'))
        if hasattr(A.TF, 'F'):
            print("A.TF.F.book:", hasattr(A.TF.F, 'book'))
            if hasattr(A.TF.F, 'book'):
                books = A.TF.F.book.freqList()
                print("First few books:", books[:5])

except Exception as e:
    print(f"Error: {e}")

# Test search
print("\nTesting search...")
try:
    results = A.search('book')
    print(f"Book search results: {len(results)} books found")
    if results:
        first_book = results[0]
        print(f"First book node: {first_book}")

        # Test getting book name
        if hasattr(A, 'F') and hasattr(A.F, 'book'):
            book_name = A.F.book.v(first_book)
            print(f"Book name: {book_name}")
        elif hasattr(A, 'TF') and hasattr(A.TF.F, 'book'):
            book_name = A.TF.F.book.v(first_book)
            print(f"Book name: {book_name}")

except Exception as e:
    print(f"Search error: {e}")