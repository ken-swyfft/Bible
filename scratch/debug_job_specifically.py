#!/usr/bin/env python3
"""Debug Job specifically and understand the node ID issue"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from tf.app import use

# Load dataset
A = use('etcbc/bhsa', silent=True)

if A:
    print("Dataset loaded")

    # List all books to find Job
    books = A.search('book')
    print("All books:")
    for book_tuple in books:
        book_id = book_tuple[0]
        book_name = A.api.F.book.v(book_id)
        print(f"  {book_name}")

    # Find Iob specifically
    print("\nLooking for Iob specifically...")
    iob_words = A.search('book book=Iob\n<< word')
    print(f"Words in Iob: {len(iob_words)}")

    if iob_words:
        print("First 10 word tuples:")
        for i, word_tuple in enumerate(iob_words[:10]):
            print(f"  {i}: {word_tuple}")

        # Check if tuples have multiple elements
        first_word = iob_words[0]
        print(f"\nFirst word tuple: {first_word}")
        print(f"Tuple length: {len(first_word)}")
        print(f"Tuple elements: {list(first_word)}")

        # Try different extraction methods
        if len(first_word) > 1:
            print("Trying different tuple elements:")
            for j, element in enumerate(first_word):
                print(f"  Element {j}: {element}")

                # Test feature access on each element
                try:
                    lex = A.api.F.lex.v(element)
                    g_word = A.api.F.g_word_utf8.v(element)
                    print(f"    lex: '{lex}', g_word: '{g_word}'")
                except Exception as e:
                    print(f"    Error: {e}")

        else:
            # Single element tuple
            word_id = first_word[0]
            print(f"Using word ID: {word_id}")

            # Test various features
            features = ['lex', 'g_lex', 'lex_utf8', 'g_lex_utf8', 'g_word', 'g_word_utf8']
            for feature in features:
                try:
                    if hasattr(A.api.F, feature):
                        value = getattr(A.api.F, feature).v(word_id)
                        print(f"  {feature}: '{value}'")
                except Exception as e:
                    print(f"  {feature}: error - {e}")

    # Also try a different approach - check node types directly
    print("\nTesting different node types:")
    try:
        # Check if we can access different node types
        all_words = A.search('word')
        print(f"Total words in corpus: {len(all_words)}")

        # Try a few random words
        test_indices = [0, 1000, 10000, 50000]
        for idx in test_indices:
            if idx < len(all_words):
                word_tuple = all_words[idx]
                word_id = word_tuple[0] if isinstance(word_tuple, tuple) else word_tuple

                lex = A.api.F.lex.v(word_id)
                g_word = A.api.F.g_word_utf8.v(word_id)

                print(f"  Word {idx} (ID {word_id}): lex='{lex}', g_word='{g_word}'")

                # If we find a working word, stop and report
                if lex or g_word:
                    print(f"    FOUND WORKING WORD AT INDEX {idx}!")
                    break

    except Exception as e:
        print(f"Node type testing error: {e}")