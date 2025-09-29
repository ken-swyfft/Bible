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

    output_file = "scratch/hebrew_features_test.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        # Get a few Job words
        book_results = A.search('book book=Iob')
        book_node = book_results[0][0]
        word_nodes = list(A.api.L.d(book_node, otype='word'))[:10]

        f.write("First 10 words from Job with all lexeme features:\n")
        f.write("="*70 + "\n\n")

        for i, word_id in enumerate(word_nodes, 1):
            f.write(f"Word {i} (ID: {word_id}):\n")

            # Try different features
            lex = A.api.F.lex.v(word_id)
            f.write(f"  lex (transliteration): {lex}\n")

            if hasattr(A.api.F, 'voc_lex_utf8'):
                voc_lex = A.api.F.voc_lex_utf8.v(word_id)
                f.write(f"  voc_lex_utf8 (vocalized): {voc_lex}\n")

            if hasattr(A.api.F, 'g_lex_utf8'):
                g_lex = A.api.F.g_lex_utf8.v(word_id)
                f.write(f"  g_lex_utf8 (consonantal): {g_lex}\n")

            if hasattr(A.api.F, 'g_word_utf8'):
                g_word = A.api.F.g_word_utf8.v(word_id)
                f.write(f"  g_word_utf8 (word form): {g_word}\n")

            f.write("\n")

        # Check available features
        f.write("="*70 + "\n")
        f.write("All available features that contain 'lex' or 'utf8':\n")
        f.write("="*70 + "\n")

        for feature in sorted(dir(A.api.F)):
            if 'lex' in feature.lower() or 'utf8' in feature.lower():
                f.write(f"  {feature}\n")

    print(f"Results written to {output_file}")

if __name__ == "__main__":
    main()