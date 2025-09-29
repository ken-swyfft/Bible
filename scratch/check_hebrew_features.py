#!/usr/bin/env python3
"""
Check what Hebrew features are available in ETCBC
"""

import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

def main():
    print("Loading ETCBC dataset...")
    from tf.app import use
    A = use('etcbc/bhsa', silent=True)

    # Get a few Job words
    book_results = A.search('book book=Iob')
    book_node = book_results[0][0]
    word_nodes = list(A.api.L.d(book_node, otype='word'))[:10]

    print("\nFirst 10 words from Job with all lexeme features:")
    print("="*70)

    for i, word_id in enumerate(word_nodes, 1):
        print(f"\nWord {i} (ID: {word_id}):")

        # Try different features
        lex = A.api.F.lex.v(word_id)
        print(f"  lex (transliteration): {lex}")

        if hasattr(A.api.F, 'voc_lex_utf8'):
            voc_lex = A.api.F.voc_lex_utf8.v(word_id)
            print(f"  voc_lex_utf8 (vocalized): {voc_lex}")

        if hasattr(A.api.F, 'g_lex_utf8'):
            g_lex = A.api.F.g_lex_utf8.v(word_id)
            print(f"  g_lex_utf8 (consonantal): {g_lex}")

        if hasattr(A.api.F, 'g_word_utf8'):
            g_word = A.api.F.g_word_utf8.v(word_id)
            print(f"  g_word_utf8 (word form): {g_word}")

    # Check available features
    print("\n" + "="*70)
    print("All available features that contain 'lex' or 'utf8':")
    print("="*70)

    for feature in sorted(dir(A.api.F)):
        if 'lex' in feature.lower() or 'utf8' in feature.lower():
            print(f"  {feature}")

if __name__ == "__main__":
    main()