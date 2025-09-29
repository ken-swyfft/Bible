#!/usr/bin/env python3
"""
Debug the actual counting logic - something is wrong with how we're counting lemmas
in the full corpus vs Job. There should definitely be rare Job vocabulary.
"""

import os
from collections import Counter

os.environ['PYTHONIOENCODING'] = 'utf-8'

def debug_counting_logic():
    """Debug the actual counting logic to find the bug."""
    print("DEBUGGING COUNTING LOGIC")
    print("=" * 40)

    try:
        from tf.app import use
        A = use('etcbc/bhsa', silent=True)

        # Extract Job lemmas first
        print("1. Extracting Job lemmas...")
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
        print(f"Job lemmas: {len(job_lemmas)} tokens, {len(job_lemma_counts)} unique")

        # Get sample of Job's rarest lemmas (appearing only once in Job)
        job_hapax = [lemma for lemma, count in job_lemma_counts.items() if count == 1]
        print(f"Job hapax legomena (appear once in Job): {len(job_hapax)}")
        print(f"Sample Job hapax: {job_hapax[:10]}")

        # Now count these specific lemmas in ALL other books
        print("\n2. Counting these Job hapax in other books...")

        # Get all books
        book_nodes = A.search('book')
        all_books = []
        for book_tuple in book_nodes:
            book_id = book_tuple[0]
            book_name = A.api.F.book.v(book_id)
            if book_name and book_name.strip():
                all_books.append(book_name.strip())

        print(f"Found {len(all_books)} books")

        # Count our sample Job hapax in other books
        hapax_in_others = Counter()

        for book in all_books:
            if book == 'Iob':
                continue  # Skip Job itself

            print(f"  Checking {book}...")
            words = A.search(f'book book={book}\n<< word')

            for word_tuple in words:
                if len(word_tuple) >= 2:
                    word_id = word_tuple[1]
                    try:
                        lemma = A.api.F.lex.v(word_id)
                        if lemma and lemma.strip():
                            lemma = lemma.strip()
                            # Only count if it's one of our Job hapax
                            if lemma in job_hapax[:20]:  # Test first 20 Job hapax
                                hapax_in_others[lemma] += 1
                    except Exception:
                        pass

        print(f"\n3. Results for first 20 Job hapax legomena:")
        for lemma in job_hapax[:20]:
            count_in_others = hapax_in_others[lemma]
            print(f"  {lemma}: appears {count_in_others} times in other books")

        # Summary
        truly_rare = sum(1 for lemma in job_hapax[:20] if hapax_in_others[lemma] < 5)
        print(f"\nOf first 20 Job hapax, {truly_rare} appear <5 times in other books")

        if truly_rare == 0:
            print("PROBLEM: Even Job hapax legomena appear frequently elsewhere!")
            print("This suggests an issue with the lemma extraction or counting logic.")
        else:
            print("GOOD: Found some truly rare vocabulary as expected.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_counting_logic()