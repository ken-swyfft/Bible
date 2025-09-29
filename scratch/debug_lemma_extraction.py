#!/usr/bin/env python3
"""Debug lemma extraction from ETCBC"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from tf.app import use

# Load dataset
A = use('etcbc/bhsa', silent=True)

if A:
    print("Dataset loaded")

    # Find Job correctly
    books = A.search('book')
    for book_tuple in books:
        book_id = book_tuple[0]
        book_name = A.api.F.book.v(book_id)
        if 'ob' in book_name.lower():
            print(f"Found Job book: '{book_name}'")

            # Get words from Job
            words = A.search(f'book book={book_name}\n<< word')
            print(f"Words in {book_name}: {len(words)}")

            if words:
                print("Testing feature access on first few words:")

                for i, word_tuple in enumerate(words[:10]):
                    word_id = word_tuple[0] if isinstance(word_tuple, tuple) else word_tuple

                    # Test different lemma features
                    features_to_test = ['lex', 'g_lex', 'lex_utf8', 'g_lex_utf8']

                    print(f"Word {i} (ID: {word_id}):")
                    for feature in features_to_test:
                        try:
                            if hasattr(A.api.F, feature):
                                value = getattr(A.api.F, feature).v(word_id)
                                print(f"  {feature}: '{value}' (type: {type(value)})")
                            else:
                                print(f"  {feature}: not available")
                        except Exception as e:
                            print(f"  {feature}: error - {e}")

                    # Also try word features
                    word_features = ['g_word_utf8', 'g_word']
                    for feature in word_features:
                        try:
                            if hasattr(A.api.F, feature):
                                value = getattr(A.api.F, feature).v(word_id)
                                print(f"  {feature}: '{value}'")
                        except Exception as e:
                            print(f"  {feature}: error - {e}")

                    print()
                    if i >= 2:  # Just test first 3 words
                        break

            break