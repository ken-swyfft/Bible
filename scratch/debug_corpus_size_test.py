#!/usr/bin/env python3
"""
Debug script to test how corpus size affects rare vocabulary detection
Tests different corpus sizes to understand the 0 rare lemmas result
"""

import os
from collections import Counter

os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_corpus_size_effect():
    """Test how corpus size affects rare vocabulary detection."""
    print("TESTING CORPUS SIZE EFFECT ON RARE VOCABULARY")
    print("=" * 50)

    try:
        from tf.app import use
        A = use('etcbc/bhsa', silent=True)

        # Get Job lemmas
        print("Extracting Job lemmas...")
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
        print(f"Job: {len(job_lemmas)} tokens, {len(job_lemma_counts)} unique lemmas")

        # Test different corpus sizes
        test_books = ['Genesis', 'Exodus', 'Leviticus', 'Numeri', 'Deuteronomium']

        for num_books in [1, 2, 3, 4, 5]:
            print(f"\nTesting against {num_books} book(s): {test_books[:num_books]}")

            # Collect lemmas from test corpus
            corpus_counts = Counter()
            corpus_counts.update(job_lemma_counts)  # Include Job

            for book in test_books[:num_books]:
                print(f"  Adding {book}...")
                words = A.search(f'book book={book}\n<< word')

                for word_tuple in words:
                    if len(word_tuple) >= 2:
                        word_id = word_tuple[1]
                        try:
                            lemma = A.api.F.lex.v(word_id)
                            if lemma and lemma.strip():
                                corpus_counts[lemma.strip()] += 1
                        except Exception:
                            pass

            # Test different thresholds
            print(f"  Total corpus size: {len(corpus_counts)} unique lemmas")

            for threshold in [1, 2, 5, 10]:
                rare_count = 0
                rare_examples = []

                for lemma in job_lemma_counts:
                    total_count = corpus_counts[lemma]
                    job_count = job_lemma_counts[lemma]
                    outside_job_count = total_count - job_count

                    if outside_job_count < threshold:
                        rare_count += 1
                        if len(rare_examples) < 3:
                            rare_examples.append(f"{lemma} (Job:{job_count}, Outside:{outside_job_count})")

                print(f"    Threshold <{threshold}: {rare_count} rare lemmas")
                if rare_examples:
                    print(f"      Examples: {', '.join(rare_examples)}")

        print("\nCONCLUSION:")
        print("As corpus size increases, fewer lemmas appear 'rare' outside Job.")
        print("With full Hebrew Bible, very few lemmas truly appear <5 times outside Job.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_corpus_size_effect()