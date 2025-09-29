#!/usr/bin/env python3
"""
Inspect individual lemmas to understand the counting issue
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

    # Pick some Job lemmas that appear rarely
    rare_in_job = [(lemma, count) for lemma, count in job_lemma_counts.items() if count <= 3]
    print(f"\nJob lemmas appearing 1-3 times in Job: {len(rare_in_job)}")

    # Sample 10 lemmas that appear once in Job
    hapax_in_job = [lemma for lemma, count in job_lemma_counts.items() if count == 1]
    print(f"Job lemmas appearing exactly once in Job: {len(hapax_in_job)}")

    # Now count these same lemmas in OTHER books
    print("\nSampling 10 Job hapax legomena and counting elsewhere...")
    print("="*70)

    sample_lemmas = hapax_in_job[:10]

    for lemma in sample_lemmas:
        print(f"\nLemma: '{lemma}'")
        print(f"  Count in Job: 1")

        # Count in all books
        total_count = 0
        book_details = []

        book_nodes = A.search('book')
        for book_tuple in book_nodes:
            book_id = book_tuple[0] if isinstance(book_tuple, tuple) else book_tuple
            book_name = A.api.F.book.v(book_id)

            if book_name:
                # Count this lemma in this book
                words = A.search(f'book book={book_name}\n<< word')
                book_count = 0
                for word_tuple in words:
                    if len(word_tuple) >= 2:
                        word_id = word_tuple[1]
                        word_lemma = A.api.F.lex.v(word_id)
                        if word_lemma == lemma:
                            book_count += 1

                if book_count > 0:
                    book_details.append((book_name, book_count))
                    total_count += book_count

        print(f"  Total count in entire Bible: {total_count}")
        print(f"  Count outside Job: {total_count - 1}")
        print(f"  Books where found:")
        for book_name, count in sorted(book_details, key=lambda x: -x[1]):
            print(f"    {book_name}: {count}")

        if total_count - 1 == 0:
            print(f"  ✓ TRUE Job hapax legomenon!")
        else:
            print(f"  ✗ NOT a hapax - appears {total_count - 1} times elsewhere")

    print("\n" + "="*70)
    print("INVESTIGATION SUMMARY:")
    print("="*70)
    print("If these Job hapax are showing high counts elsewhere, we have a bug.")
    print("If they show 0 counts elsewhere, the algorithm is correct but may")
    print("need a higher threshold to find interesting rare vocabulary.")

if __name__ == "__main__":
    main()