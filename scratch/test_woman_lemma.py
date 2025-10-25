"""Test to find the correct lemma for woman (אִשָּׁה)."""

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

# Check Proverbs 31:10 which has "eshet chayil"
print("Checking Proverbs 31:10 (אֵשֶׁת חַיִל)...")
print("=" * 80)

verse_results = A.search('verse book=Proverbia chapter=31 verse=10')
if verse_results:
    verse_node = verse_results[0][0] if isinstance(verse_results[0], tuple) else verse_results[0]
    word_nodes = A.api.L.d(verse_node, otype='word')

    print(f"\nFound {len(word_nodes)} words:\n")

    for i, word in enumerate(word_nodes):
        g_word = A.api.F.g_word_utf8.v(word) or ""
        lex = A.api.F.lex.v(word) or ""
        voc_lex = A.api.F.voc_lex_utf8.v(word) or ""

        print(f"Word {i+1}: {g_word}")
        print(f"  Lemma: {lex}")
        print(f"  Voc lemma: {voc_lex}")
        print()
