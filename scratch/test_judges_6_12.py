"""Test to see the structure of Judges 6:12."""

import os
import sys

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from tf.app import use

print("Loading ETCBC dataset...")
A = use('etcbc/bhsa', silent=True)
print("Dataset loaded\n")

# Check Judges 6:12
print("Checking Judges 6:12 (גִּבּוֹר הֶחָיִל)...")
print("=" * 80)

# Try to find Judges - check book names
verse_results = A.search('verse chapter=6 verse=12')
found_judges = None
for result in verse_results:
    verse_node = result[0] if isinstance(result, tuple) else result
    book = A.api.F.book.v(verse_node)
    if 'Judic' in book or 'Judg' in book:
        found_judges = verse_node
        print(f"Found in book: {book}\n")
        break

if found_judges:
    word_nodes = A.api.L.d(found_judges, otype='word')

    print(f"Found {len(word_nodes)} words:\n")

    for i, word in enumerate(word_nodes):
        g_word = A.api.F.g_word_utf8.v(word) or ""
        lex = A.api.F.lex.v(word) or ""
        voc_lex = A.api.F.voc_lex_utf8.v(word) or ""

        print(f"Word {i+1}: {g_word}")
        print(f"  Lemma: {lex}")
        print(f"  Voc lemma: {voc_lex}")

        # Check if this word or next is related to our target
        if lex in ['GBWR/', 'XJL/', '>JC/', '>CH/']:
            print(f"  *** TARGET WORD ***")
        print()
