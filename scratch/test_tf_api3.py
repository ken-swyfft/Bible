#!/usr/bin/env python3
"""Test script to find Job and understand search syntax"""

from tf.app import use

# Load dataset
A = use('etcbc/bhsa', silent=True)

# List all books to find Job
print("All books in the corpus:")
books = A.api.F.book.freqList()
for freq, book in books:
    print(f"  {book}: {freq} chapters")

# Search for Job specifically
job_books = A.search('book book=Job')
print(f"\nSearch results for 'book book=Job': {len(job_books)} results")

# Try different variations
variations = ['Iobus', 'Hiob', 'Ijob', 'Job']
for variation in variations:
    results = A.search(f'book book={variation}')
    print(f"Search for '{variation}': {len(results)} results")

# Test word search with correct syntax
print("\nTesting word search syntax...")
try:
    words = A.search('''
    word
    ''')
    print(f"Total words in corpus: {len(words)}")

    # Test getting book of first word
    if words:
        first_word = words[0]
        # Try to find what book this word belongs to
        book_results = A.search(f'''
        book
        //* word
        ''')
        print(f"Book query test: {len(book_results)} results")

except Exception as e:
    print(f"Error: {e}")

# Try a different approach - get books directly and then find words
print("\nTrying direct book node approach...")
book_nodes = A.search('book')
print(f"Found {len(book_nodes)} book nodes")

if book_nodes:
    for book_node in book_nodes[:5]:  # Test first 5 books
        book_name = A.api.F.book.v(book_node)
        print(f"Book node {book_node}: '{book_name}'")