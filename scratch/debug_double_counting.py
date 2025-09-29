#!/usr/bin/env python3
"""
Check if we're accidentally double-counting Job or have other counting issues.
The fact that Job hapax appear 27+ times elsewhere suggests a major bug.
"""

import os
from collections import Counter

os.environ['PYTHONIOENCODING'] = 'utf-8'

def debug_double_counting():
    """Check for double-counting issues."""
    print("DEBUGGING DOUBLE-COUNTING ISSUES")
    print("=" * 40)

    try:
        from tf.app import use
        A = use('etcbc/bhsa', silent=True)

        # Get one specific Job hapax to trace through the logic
        print("1. Getting a specific Job hapax to trace...")

        job_words = A.search('book book=Iob\n<< word')
        job_lemmas = []
        for word_tuple in job_words:
            if len(word_tuple) >= 2:
                word_id = word_tuple[1]
                try:
                    lemma = A.api.F.lex.v(word_id)
                    if lemma and lemma.strip():
                        job_lemmas.append(lemma.strip())
                except Exception:
                    pass

        job_lemma_counts = Counter(job_lemmas)

        # Pick a specific hapax to trace
        hapax_to_trace = None
        for lemma, count in job_lemma_counts.items():
            if count == 1:
                hapax_to_trace = lemma
                break

        print(f"Tracing lemma: '{hapax_to_trace}' (appears 1x in Job)")

        # Method 1: Count this lemma across ALL books (including Job)
        print(f"\n2. Method 1: Count '{hapax_to_trace}' across ALL books...")
        all_books_count = 0

        book_nodes = A.search('book')
        for book_tuple in book_nodes:
            book_id = book_tuple[0]
            book_name = A.api.F.book.v(book_id)
            if book_name and book_name.strip():
                words = A.search(f'book book={book_name.strip()}\n<< word')
                book_count = 0

                for word_tuple in words:
                    if len(word_tuple) >= 2:
                        word_id = word_tuple[1]
                        try:
                            lemma = A.api.F.lex.v(word_id)
                            if lemma and lemma.strip() == hapax_to_trace:
                                book_count += 1
                                all_books_count += 1
                        except Exception:
                            pass

                if book_count > 0:
                    print(f"  {book_name}: {book_count} occurrences")

        print(f"Total across all books: {all_books_count}")

        # Method 2: Count ONLY in non-Job books
        print(f"\n3. Method 2: Count '{hapax_to_trace}' in non-Job books only...")
        non_job_count = 0

        for book_tuple in book_nodes:
            book_id = book_tuple[0]
            book_name = A.api.F.book.v(book_id)
            if book_name and book_name.strip() and book_name.strip() != 'Iob':
                words = A.search(f'book book={book_name.strip()}\n<< word')
                book_count = 0

                for word_tuple in words:
                    if len(word_tuple) >= 2:
                        word_id = word_tuple[1]
                        try:
                            lemma = A.api.F.lex.v(word_id)
                            if lemma and lemma.strip() == hapax_to_trace:
                                book_count += 1
                                non_job_count += 1
                        except Exception:
                            pass

                if book_count > 0:
                    print(f"  {book_name}: {book_count} occurrences")

        print(f"Total in non-Job books: {non_job_count}")

        # Method 3: Check if there are any actual hapax legomena in the corpus
        print(f"\n4. Looking for TRUE corpus hapax legomena...")

        # Count all lemmas in entire corpus
        all_lemmas = []
        for book_tuple in book_nodes:
            book_id = book_tuple[0]
            book_name = A.api.F.book.v(book_id)
            if book_name and book_name.strip():
                words = A.search(f'book book={book_name.strip()}\n<< word')

                for word_tuple in words:
                    if len(word_tuple) >= 2:
                        word_id = word_tuple[1]
                        try:
                            lemma = A.api.F.lex.v(word_id)
                            if lemma and lemma.strip():
                                all_lemmas.append(lemma.strip())
                        except Exception:
                            pass

        all_lemma_counts = Counter(all_lemmas)
        true_hapax = [lemma for lemma, count in all_lemma_counts.items() if count == 1]

        print(f"TRUE hapax in entire Hebrew Bible: {len(true_hapax)}")
        if true_hapax:
            print(f"Sample true hapax: {true_hapax[:5]}")

            # Check if any of these are in Job
            job_hapax_in_corpus = [lemma for lemma in true_hapax if lemma in job_lemma_counts]
            print(f"Job contains {len(job_hapax_in_corpus)} true corpus hapax")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_double_counting()