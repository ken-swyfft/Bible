#!/usr/bin/env python3
"""
Verify the fix: Check corpus hapax count with corrected method
"""

import os
import sys
from collections import Counter

os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

def main():
    print("Loading ETCBC dataset...")
    from tf.app import use
    A = use('etcbc/bhsa', silent=True)

    print("\nCounting all lemmas across entire Bible using FIXED method (L.d)...")

    book_nodes = A.search('book')
    all_books = []
    for book_tuple in book_nodes:
        book_id = book_tuple[0] if isinstance(book_tuple, tuple) else book_tuple
        book_name = A.api.F.book.v(book_id)
        if book_name and book_name.strip():
            all_books.append((book_name.strip(), book_id))

    all_lemmas = []
    total_words = 0

    for book_name, book_id in all_books:
        word_nodes = A.api.L.d(book_id, otype='word')
        for word_id in word_nodes:
            lemma = A.api.F.lex.v(word_id)
            if lemma and lemma.strip():
                all_lemmas.append(lemma.strip())
                total_words += 1

    print(f"\nTotal words in Bible: {total_words}")
    print(f"Unique lemmas: {len(set(all_lemmas))}")

    # Count hapax
    lemma_counts = Counter(all_lemmas)
    hapax = [lemma for lemma, count in lemma_counts.items() if count == 1]

    print(f"\nCorpus hapax legomena (appearing exactly once): {len(hapax)}")

    if len(hapax) > 1000:
        print("✓ This looks correct! Hebrew Bible typically has ~1500-2000 hapax.")
    else:
        print(f"⚠ This is still low. Expected ~1500-2000 hapax.")

    print(f"\nFirst 10 hapax:")
    for i, lemma in enumerate(hapax[:10], 1):
        print(f"  {i:2d}. {lemma}")

if __name__ == "__main__":
    main()