#!/usr/bin/env python3
"""Final test to get the correct Text-Fabric approach"""

from tf.app import use

# Load dataset
A = use('etcbc/bhsa', silent=True)

# Test the correct approach
print("Testing correct search approach...")

# Method 1: Get all words in Iob
words_in_iob = A.search('book book=Iob\n<< word')
print(f"Words in Iob: {len(words_in_iob)}")

if words_in_iob:
    # Test getting lexemes
    lexemes = []
    for i, word in enumerate(words_in_iob[:20]):  # First 20 words
        lexeme = A.api.F.lex.v(word)
        if lexeme:
            lexemes.append(lexeme)
    print(f"First 20 lexemes: {lexemes}")

# Test book name extraction
print("\nTesting book names...")
book_nodes = A.search('book')
for book_node in book_nodes[:5]:
    book_name = A.api.F.book.v(book_node)
    print(f"Book: {book_name}")

# Test correct freqList usage
print("\nTesting freqList...")
freq_list = A.api.F.book.freqList()
print("Type of freq_list:", type(freq_list))
print("First 5 items:", freq_list[:5])

# Check how to get book names properly
print("\nAll unique book names:")
unique_books = set()
for book_node in book_nodes:
    book_name = A.api.F.book.v(book_node)
    if book_name:
        unique_books.add(book_name)
print(sorted(unique_books))