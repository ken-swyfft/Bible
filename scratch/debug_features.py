#!/usr/bin/env python3
"""Debug Text-Fabric features"""

from tf.app import use

# Load dataset
A = use('etcbc/bhsa', silent=True)

# Get a few words and test all features
words = A.search('word')
print(f"Total words: {len(words)}")

if words:
    test_word = words[0]
    print(f"\nTesting features on word node {test_word}:")

    # Test all available features
    features_to_test = ['lex', 'g_lex', 'lex_utf8', 'g_lex_utf8', 'g_word', 'g_word_utf8', 'txt', 'gloss']

    for feature in features_to_test:
        try:
            value = getattr(A.api.F, feature).v(test_word)
            print(f"  {feature}: {value}")
        except:
            print(f"  {feature}: ERROR")

    # Test getting the book for this word
    print(f"\nFinding book for word {test_word}:")

    # Method 1: Use L (locality) to go up to book
    try:
        book_node = A.api.L.u(test_word, 'book')[0]  # Go up to book level
        print(f"Book node: {book_node}")

        # Now get book name
        book_name = A.api.F.book.v(book_node)
        print(f"Book name: {book_name}")
    except Exception as e:
        print(f"Error getting book: {e}")

# Test direct book approach
print(f"\nTesting books directly:")
books = A.search('book')
if books:
    first_book = books[0]
    print(f"First book node: {first_book}")

    # Try different ways to get book name
    book_name1 = A.api.F.book.v(first_book)
    print(f"Method 1 - book name: '{book_name1}'")

    # Check if book name is in a different attribute
    try:
        for attr in dir(A.api.F):
            if 'book' in attr.lower():
                feature = getattr(A.api.F, attr)
                value = feature.v(first_book)
                print(f"  {attr}: '{value}'")
    except Exception as e:
        print(f"Error testing book attributes: {e}")

print("\nAll available features:")
all_features = [attr for attr in dir(A.api.F) if not attr.startswith('_')]
print(all_features[:20])  # First 20