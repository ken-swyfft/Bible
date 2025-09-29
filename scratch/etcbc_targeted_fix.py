#!/usr/bin/env python3
"""
ETCBC BHSA Targeted Fix

Based on diagnosis, the issue is:
1. Data exists and loads successfully
2. Search finds nodes correctly
3. Feature access returns None instead of values

This suggests a node ID or API access pattern issue.
"""

import os
from pathlib import Path

def test_node_id_formats():
    """Test different ways to access node data"""
    print("TESTING NODE ID FORMATS")
    print("-" * 40)

    try:
        from tf.app import use

        # Load with silent mode
        A = use('etcbc/bhsa', silent=True)

        if A and hasattr(A, 'api'):
            print("App loaded successfully")

            # Get books
            books = A.search('book')
            print(f"Found {len(books)} books")

            if books:
                # Test different node access patterns
                first_book = books[0]
                print(f"First book node: {first_book} (type: {type(first_book)})")

                # Pattern 1: Direct tuple access (if node is tuple)
                if isinstance(first_book, tuple):
                    print("Node is tuple - trying first element")
                    node_id = first_book[0] if len(first_book) > 0 else first_book
                    print(f"Node ID: {node_id}")

                    try:
                        book_name = A.api.F.book.v(node_id)
                        print(f"Book name (ID): '{book_name}'")
                    except Exception as e:
                        print(f"ID access error: {e}")

                # Pattern 2: Try the tuple directly
                try:
                    book_name = A.api.F.book.v(first_book)
                    print(f"Book name (tuple): '{book_name}'")
                except Exception as e:
                    print(f"Tuple access error: {e}")

                # Pattern 3: Check if we need to iterate through results
                print("Testing all book nodes:")
                for i, book in enumerate(books[:5]):  # First 5 books
                    try:
                        # Try both tuple and individual access
                        name1 = A.api.F.book.v(book)

                        if isinstance(book, tuple) and len(book) > 0:
                            name2 = A.api.F.book.v(book[0])
                        else:
                            name2 = "N/A"

                        print(f"  Book {i}: {book} -> '{name1}' / '{name2}'")

                        # If we find a working name, investigate further
                        if name1 and name1 != 'None':
                            print(f"SUCCESS: Found working book name: '{name1}'")
                            return A, book
                        elif name2 and name2 != 'None':
                            print(f"SUCCESS: Found working book name: '{name2}'")
                            return A, book[0]

                    except Exception as e:
                        print(f"  Book {i} error: {e}")

                # Pattern 4: Try other features to see if any work
                print("\nTesting other features on first book:")
                test_features = ['book@en', 'book@he', 'chapter', 'verse']
                for feature in test_features:
                    try:
                        if hasattr(A.api.F, feature):
                            value = getattr(A.api.F, feature).v(first_book)
                            print(f"  {feature}: '{value}'")
                        else:
                            print(f"  {feature}: feature not available")
                    except Exception as e:
                        print(f"  {feature}: error - {e}")

        return None, None

    except Exception as e:
        print(f"General error: {e}")
        return None, None

def test_alternative_node_access():
    """Test alternative ways to access nodes and features"""
    print("\nTESTING ALTERNATIVE NODE ACCESS")
    print("-" * 40)

    try:
        from tf.fabric import Fabric

        home = Path.home()
        tf_path = str(home / 'text-fabric-data' / 'github' / 'etcbc' / 'bhsa' / 'tf' / '2021')

        # Load with specific features
        TF = Fabric(locations=[tf_path], silent=True)
        api = TF.load('book lex g_word_utf8', silent=True)

        if api:
            print("Direct Fabric loading successful")

            # Get node ranges for different types
            print("Node type information:")
            for otype in ['book', 'word', 'lex']:
                try:
                    # Get nodes of this type using TF.nodesByOtype
                    if hasattr(TF, 'nodesByOtype'):
                        nodes = TF.nodesByOtype[otype] if otype in TF.nodesByOtype else []
                        print(f"  {otype}: {len(nodes)} nodes")

                        if nodes:
                            first_node = nodes[0]
                            print(f"    First {otype} node: {first_node}")

                            # Test feature access
                            if otype == 'book':
                                try:
                                    book_name = api.F.book.v(first_node)
                                    print(f"    Book name: '{book_name}'")

                                    if book_name and book_name != 'None':
                                        print(f"SUCCESS: Direct fabric access works!")
                                        return api, first_node
                                except Exception as e:
                                    print(f"    Feature access error: {e}")

                except Exception as e:
                    print(f"  {otype} error: {e}")

    except Exception as e:
        print(f"Alternative access error: {e}")

    return None, None

def test_feature_list_and_values():
    """Test what features are available and have actual data"""
    print("\nTESTING FEATURE AVAILABILITY")
    print("-" * 40)

    try:
        from tf.app import use
        A = use('etcbc/bhsa', silent=True)

        if A and hasattr(A, 'api'):
            # Get a sample of different node types
            books = A.search('book')
            words = A.search('word')

            print(f"Testing on {len(books)} books and {len(words)} words")

            if books and words:
                sample_book = books[0]
                sample_word = words[0]

                # Test a variety of features
                features_to_test = [
                    ('book', sample_book),
                    ('g_word_utf8', sample_word),
                    ('lex', sample_word),
                    ('g_lex_utf8', sample_word)
                ]

                for feature_name, node in features_to_test:
                    try:
                        if hasattr(A.api.F, feature_name):
                            feature_obj = getattr(A.api.F, feature_name)
                            value = feature_obj.v(node)
                            value_type = type(value)

                            print(f"  {feature_name} on {node}: '{value}' (type: {value_type})")

                            # If we find a non-None value, this is progress!
                            if value is not None and str(value) != 'None':
                                print(f"    SUCCESS: Found working feature!")

                                # Try to get more values from this feature
                                print(f"    Testing more {feature_name} values:")

                                if feature_name == 'book':
                                    for i, book in enumerate(books[:3]):
                                        val = feature_obj.v(book)
                                        print(f"      Book {i}: '{val}'")

                                elif feature_name in ['g_word_utf8', 'lex', 'g_lex_utf8']:
                                    for i, word in enumerate(words[:3]):
                                        val = feature_obj.v(word)
                                        print(f"      Word {i}: '{val}'")

                                return A, (feature_name, node, value)

                        else:
                            print(f"  {feature_name}: not available")

                    except Exception as e:
                        print(f"  {feature_name} error: {e}")

    except Exception as e:
        print(f"Feature testing error: {e}")

    return None, None

def run_targeted_fix():
    """Run all targeted fix attempts"""
    print("ETCBC BHSA TARGETED FIX")
    print("=" * 50)

    # Method 1: Test node ID formats
    result1 = test_node_id_formats()
    if result1[0]:
        print("\nFIX FOUND: Node ID format issue resolved!")
        return result1

    # Method 2: Alternative node access
    result2 = test_alternative_node_access()
    if result2[0]:
        print("\nFIX FOUND: Alternative access method works!")
        return result2

    # Method 3: Feature testing
    result3 = test_feature_list_and_values()
    if result3[0]:
        print("\nFIX FOUND: Working feature identified!")
        return result3

    print("\nNO FIX FOUND: All methods still return None")
    print("This suggests a deeper data corruption or version compatibility issue")
    return None, None

if __name__ == "__main__":
    result = run_targeted_fix()

    if result[0]:
        print(f"\nSUCCESS: Working ETCBC connection established!")
        print(f"Working method details: {result[1]}")
    else:
        print(f"\nFAILED: No working connection found")
        print("Recommendation: Try reinstalling Text-Fabric or using a different ETCBC version")