#!/usr/bin/env python3
"""
Debug script to understand why we're getting 0 rare Job lemmas
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

    # Extract Job lemmas
    print("\nExtracting Job lemmas...")
    job_words = A.search('book book=Iob\n<< word')
    job_lemmas = []
    for word_tuple in job_words:
        if len(word_tuple) >= 2:
            word_id = word_tuple[1]
            lemma = A.api.F.lex.v(word_id)
            if lemma and lemma.strip():
                job_lemmas.append(lemma.strip())

    job_lemma_counts = Counter(job_lemmas)
    print(f"Job has {len(job_lemmas)} tokens, {len(job_lemma_counts)} unique lemmas")

    # Get all books except Job
    print("\nGetting all books...")
    book_nodes = A.search('book')
    all_books = []
    for book_tuple in book_nodes:
        book_id = book_tuple[0] if isinstance(book_tuple, tuple) else book_tuple
        book_name = A.api.F.book.v(book_id)
        if book_name and book_name.strip() and book_name != 'Iob':
            all_books.append(book_name.strip())

    print(f"Found {len(all_books)} books (excluding Job)")

    # Count lemmas ONLY in non-Job books
    print("\nCounting lemmas in non-Job books...")
    non_job_lemma_counts = Counter()

    for i, book in enumerate(all_books, 1):
        print(f"Processing {book} ({i}/{len(all_books)})...", end=' ')
        words = A.search(f'book book={book}\n<< word')
        lemmas = []
        for word_tuple in words:
            if len(word_tuple) >= 2:
                word_id = word_tuple[1]
                lemma = A.api.F.lex.v(word_id)
                if lemma and lemma.strip():
                    lemmas.append(lemma.strip())

        for lemma in lemmas:
            non_job_lemma_counts[lemma] += 1
        print(f"{len(lemmas)} tokens")

    print(f"\nTotal unique lemmas in non-Job books: {len(non_job_lemma_counts)}")

    # Find Job lemmas that are rare outside Job
    print("\nFinding rare Job lemmas...")
    rare_lemmas = []

    for lemma, job_count in job_lemma_counts.items():
        outside_count = non_job_lemma_counts.get(lemma, 0)
        if outside_count < 5:
            rare_lemmas.append((lemma, job_count, outside_count))

    print(f"Found {len(rare_lemmas)} rare Job lemmas (appearing <5 times outside Job)")

    # Show some examples
    print("\nFirst 20 rare Job lemmas:")
    rare_lemmas.sort(key=lambda x: x[2])  # Sort by outside count
    for i, (lemma, job_count, outside_count) in enumerate(rare_lemmas[:20], 1):
        print(f"{i:2d}. {lemma:<30} Job: {job_count:3d}, Elsewhere: {outside_count}")

    # Check hapax legomena in entire corpus
    print("\n" + "="*60)
    print("CORPUS-WIDE HAPAX CHECK:")
    print("="*60)

    all_lemma_counts = Counter(job_lemmas)
    for book in all_books:
        words = A.search(f'book book={book}\n<< word')
        for word_tuple in words:
            if len(word_tuple) >= 2:
                word_id = word_tuple[1]
                lemma = A.api.F.lex.v(word_id)
                if lemma and lemma.strip():
                    all_lemma_counts[lemma.strip()] += 1

    hapax = [lemma for lemma, count in all_lemma_counts.items() if count == 1]
    print(f"Total hapax legomena (appearing exactly once in entire corpus): {len(hapax)}")

    if len(hapax) < 100:
        print("\nWARNING: This is way too low! Hebrew Bible should have ~1500+ hapax")
        print("This suggests data duplication or counting error.")

    print("\nFirst 10 corpus hapax:")
    for i, lemma in enumerate(hapax[:10], 1):
        print(f"{i:2d}. {lemma}")

if __name__ == "__main__":
    main()