#!/usr/bin/env python3
"""
Check a specific lemma: MLJYH/
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

    test_lemma = "MLJYH/"

    print(f"\n{'='*70}")
    print(f"Testing lemma: '{test_lemma}'")
    print(f"{'='*70}")

    # Count in each book
    book_nodes = A.search('book')
    all_books = []
    for book_tuple in book_nodes:
        book_id = book_tuple[0] if isinstance(book_tuple, tuple) else book_tuple
        book_name = A.api.F.book.v(book_id)
        if book_name and book_name.strip():
            all_books.append(book_name.strip())

    total_count = 0
    books_with_lemma = []

    for book in all_books:
        words = A.search(f'book book={book}\n<< word')
        count = 0
        for word_tuple in words:
            if len(word_tuple) >= 2:
                word_id = word_tuple[1]
                lemma = A.api.F.lex.v(word_id)
                if lemma == test_lemma:
                    count += 1

        if count > 0:
            books_with_lemma.append((book, count))
            total_count += count

    print(f"\nTotal occurrences of '{test_lemma}': {total_count}")
    print(f"Books where '{test_lemma}' appears:")
    for book, count in books_with_lemma:
        marker = " <-- JOB" if book == "Iob" else ""
        print(f"  {book:<20} {count:3d} times{marker}")

    print(f"\nCount in Job: {next((c for b, c in books_with_lemma if b == 'Iob'), 0)}")
    job_count = next((c for b, c in books_with_lemma if b == 'Iob'), 0)
    print(f"Count outside Job: {total_count - job_count}")

    # Now test the ACTUAL logic from the main script
    print(f"\n{'='*70}")
    print("TESTING MAIN SCRIPT LOGIC:")
    print(f"{'='*70}")

    # Replicate main script counting
    all_lemma_counts = Counter()
    job_lemmas = []

    for book in all_books:
        print(f"Processing {book}...", end=' ')
        words = A.search(f'book book={book}\n<< word')
        lemmas = []
        for word_tuple in words:
            if len(word_tuple) >= 2:
                word_id = word_tuple[1]
                lemma = A.api.F.lex.v(word_id)
                if lemma and lemma.strip():
                    lemmas.append(lemma.strip())

        if book == 'Iob':
            job_lemmas = lemmas

        for lemma in lemmas:
            all_lemma_counts[lemma] += 1

        print(f"{len(lemmas)} tokens")

    job_lemma_counts = Counter(job_lemmas)

    print(f"\nFor lemma '{test_lemma}':")
    print(f"  all_lemma_counts['{test_lemma}']: {all_lemma_counts[test_lemma]}")
    print(f"  job_lemma_counts['{test_lemma}']: {job_lemma_counts[test_lemma]}")
    print(f"  outside_job_count: {all_lemma_counts[test_lemma] - job_lemma_counts[test_lemma]}")

    if test_lemma in job_lemma_counts:
        outside_count = all_lemma_counts[test_lemma] - job_lemma_counts[test_lemma]
        if outside_count < 5:
            print(f"  ✓ SHOULD be classified as rare (outside_count = {outside_count} < 5)")
        else:
            print(f"  ✗ NOT classified as rare (outside_count = {outside_count} >= 5)")

    # Count how many Job lemmas are truly rare
    print(f"\n{'='*70}")
    print("FULL ANALYSIS:")
    print(f"{'='*70}")

    rare_count = 0
    for lemma in job_lemma_counts:
        outside_count = all_lemma_counts[lemma] - job_lemma_counts[lemma]
        if outside_count < 5:
            rare_count += 1

    print(f"Total Job lemmas: {len(job_lemma_counts)}")
    print(f"Rare Job lemmas (appearing <5 times outside): {rare_count}")

    if rare_count == 0:
        print("\n⚠ WARNING: 0 rare lemmas found!")
        print("This means EVERY Job lemma appears 5+ times outside Job.")
        print("Let me check the minimum outside count...")

        min_outside = float('inf')
        min_lemma = None
        for lemma in job_lemma_counts:
            outside_count = all_lemma_counts[lemma] - job_lemma_counts[lemma]
            if outside_count < min_outside:
                min_outside = outside_count
                min_lemma = lemma

        print(f"\nRarest Job lemma: '{min_lemma}'")
        print(f"  Appears {job_lemma_counts[min_lemma]} times in Job")
        print(f"  Appears {min_outside} times outside Job")

if __name__ == "__main__":
    main()