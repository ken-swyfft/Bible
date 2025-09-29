#!/usr/bin/env python3
"""Debug Text-Fabric data loading"""

from tf.app import use

print("Loading with debugging...")

# Try loading with more verbose output
A = use('etcbc/bhsa')  # Remove silent=True to see loading messages

print("Available methods on A:")
methods = [m for m in dir(A) if not m.startswith('_')]
print(methods)

print("\nAPI object info:")
if hasattr(A, 'api'):
    print(f"API exists: {A.api}")
    print(f"API type: {type(A.api)}")

    if hasattr(A.api, 'TF'):
        print(f"TF object: {A.api.TF}")
        print(f"TF loaded: {A.api.TF.isLoaded}")

        # Check if features are loaded
        print(f"Features loaded: {list(A.api.TF.features.keys())[:10]}")

print("\nTrying manual search:")
try:
    result = A.search('word')
    print(f"Word search result: {len(result)} words")

    if result:
        word = result[0]
        print(f"First word: {word}")

        # Try accessing word text directly from TF
        if hasattr(A.api, 'TF'):
            tf = A.api.TF
            if 'g_word_utf8' in tf.features:
                word_text = tf.features['g_word_utf8'].v(word)
                print(f"Word text: {word_text}")
except Exception as e:
    print(f"Error in search: {e}")

# Try the show method which might work better
print("\nTrying show method:")
try:
    words = A.search('word')
    if words:
        A.show(words[:3])  # Show first 3 words
except Exception as e:
    print(f"Error in show: {e}")