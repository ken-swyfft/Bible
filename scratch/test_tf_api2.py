#!/usr/bin/env python3
"""Test script to understand Text-Fabric API structure"""

from tf.app import use

# Load dataset
A = use('etcbc/bhsa', silent=True)

print("A.api attributes:")
print([attr for attr in dir(A.api) if not attr.startswith('_')])

# Test accessing features through api
if hasattr(A.api, 'F'):
    print("\nA.api.F available")
    print("A.api.F attributes:", [attr for attr in dir(A.api.F) if not attr.startswith('_')])

    if hasattr(A.api.F, 'book'):
        print("\nBook feature available")
        books = A.api.F.book.freqList()
        print("First few books:", books[:5])

        # Test getting a book name
        results = A.search('book')
        if results:
            first_book = results[0]
            book_name = A.api.F.book.v(first_book)
            print(f"First book name: {book_name}")

# Test word search in Job
print("\nSearching for words in Job...")
job_words = A.search('''
book book=Job
<< word
''')
print(f"Found {len(job_words)} words in Job")

if job_words and hasattr(A.api.F, 'lex'):
    print("Testing lexeme extraction...")
    first_few_lexemes = []
    for word in job_words[:10]:
        lexeme = A.api.F.lex.v(word)
        first_few_lexemes.append(lexeme)
    print("First 10 lexemes:", first_few_lexemes)