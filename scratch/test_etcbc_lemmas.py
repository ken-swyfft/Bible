"""Test script to explore ETCBC lemmas for חיל words."""

import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from tf.app import use

print("Loading ETCBC dataset...")
A = use('etcbc/bhsa', silent=True)
print("Dataset loaded\n")

# Let's search for a known verse: Ruth 2:1 which has "gibbor chayil"
print("Looking at Ruth 2:1 (known to have גִּבּוֹר חַיִל)...")
print("=" * 80)

# Search for Ruth 2:1
verse_results = A.search('verse book=Ruth chapter=2 verse=1')
if verse_results:
    verse_node = verse_results[0][0] if isinstance(verse_results[0], tuple) else verse_results[0]

    # Get all words in this verse
    word_nodes = A.api.L.d(verse_node, otype='word')

    print(f"\nFound {len(word_nodes)} words in Ruth 2:1:\n")

    for i, word in enumerate(word_nodes):
        # Get various features
        g_word = A.api.F.g_word_utf8.v(word) or ""
        lex = A.api.F.lex.v(word) or ""
        voc_lex = A.api.F.voc_lex_utf8.v(word) or ""

        print(f"Word {i+1}:")
        print(f"  Hebrew: {g_word}")
        print(f"  Lemma (lex): {lex}")
        print(f"  Vocalized lemma: {voc_lex}")
        print()

print("\n" + "=" * 80)
print("Looking at Judges 20:44 (should have אַנְשֵׁי־חָיִל)...")
print("=" * 80)

# First, let's see what books are available
print("\nChecking available book names...")
book_results = A.search('book')
books = set()
for b in book_results[:5]:  # Just check first 5
    book_node = b[0] if isinstance(b, tuple) else b
    book_name = A.api.F.book.v(book_node)
    books.add(book_name)
    print(f"  Sample book: {book_name}")

# Search for Judges 20:44 - try different book names
for book_name in ['Judges', 'Judicum', 'Jud']:
    verse_results = A.search(f'verse book={book_name} chapter=20 verse=44')
    if verse_results:
        print(f"\n✓ Found with book name: {book_name}")
        break
else:
    print("\nTrying without specifying book name...")
    verse_results = A.search('verse chapter=20 verse=44')

if verse_results:
    verse_node = verse_results[0][0] if isinstance(verse_results[0], tuple) else verse_results[0]

    # Get all words in this verse
    word_nodes = A.api.L.d(verse_node, otype='word')

    print(f"\nFound {len(word_nodes)} words in Judges 20:44:\n")

    for i, word in enumerate(word_nodes):
        # Get various features
        g_word = A.api.F.g_word_utf8.v(word) or ""
        lex = A.api.F.lex.v(word) or ""
        voc_lex = A.api.F.voc_lex_utf8.v(word) or ""

        print(f"Word {i+1}:")
        print(f"  Hebrew: {g_word}")
        print(f"  Lemma (lex): {lex}")
        print(f"  Vocalized lemma: {voc_lex}")
        print()
