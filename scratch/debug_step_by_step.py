#!/usr/bin/env python3
"""
Step-by-step debugging of ETCBC rare vocabulary detection
Following AGENTS.md guidance: break down into small pieces and test each step
"""

import os
from collections import Counter

os.environ['PYTHONIOENCODING'] = 'utf-8'

def step1_basic_connection():
    """Step 1: Test basic ETCBC connection"""
    print("STEP 1: Testing basic ETCBC connection")
    print("-" * 40)

    try:
        from tf.app import use
        A = use('etcbc/bhsa', silent=True)

        if A and hasattr(A, 'api'):
            print("SUCCESS: ETCBC connection successful")
            return A
        else:
            print("FAILED: ETCBC connection failed")
            return None
    except Exception as e:
        print(f"FAILED: ETCBC connection error: {e}")
        return None

def step2_job_lemma_extraction(A):
    """Step 2: Test Job lemma extraction specifically"""
    print("\nSTEP 2: Testing Job lemma extraction")
    print("-" * 40)

    try:
        # Get Job words
        job_words = A.search('book book=Iob\n<< word')
        print(f"Found {len(job_words)} word tokens in Job")

        # Test extraction on small sample first
        sample_lemmas = []
        for i, word_tuple in enumerate(job_words[:100]):
            if len(word_tuple) >= 2:
                word_id = word_tuple[1]
                try:
                    lemma = A.api.F.lex.v(word_id)
                    if lemma and lemma.strip():
                        sample_lemmas.append(lemma.strip())
                except Exception:
                    pass

        print(f"SUCCESS: Extracted {len(sample_lemmas)} lemmas from first 100 words")
        print(f"Sample lemmas: {sample_lemmas[:10]}")

        if len(sample_lemmas) > 0:
            return True
        else:
            print("FAILED: No lemmas extracted from sample")
            return False

    except Exception as e:
        print(f"FAILED: Job extraction error: {e}")
        return False

def step3_full_job_extraction(A):
    """Step 3: Extract all Job lemmas"""
    print("\nSTEP 3: Full Job lemma extraction")
    print("-" * 40)

    try:
        job_words = A.search('book book=Iob\n<< word')
        job_lemmas = []

        print("Extracting all Job lemmas...")
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
        print(f"SUCCESS: Total Job lemmas: {len(job_lemmas)}")
        print(f"SUCCESS: Unique Job lemmas: {len(job_lemma_counts)}")
        print(f"Most common Job lemmas: {job_lemma_counts.most_common(5)}")

        return job_lemma_counts

    except Exception as e:
        print(f"FAILED: Full extraction error: {e}")
        return None

def step4_test_other_book(A, book_name="Genesis"):
    """Step 4: Test extraction from another book"""
    print(f"\nSTEP 4: Testing {book_name} extraction")
    print("-" * 40)

    try:
        book_words = A.search(f'book book={book_name}\n<< word')
        print(f"Found {len(book_words)} words in {book_name}")

        # Extract sample
        book_lemmas = []
        for word_tuple in book_words[:1000]:  # Sample
            if len(word_tuple) >= 2:
                word_id = word_tuple[1]
                try:
                    lemma = A.api.F.lex.v(word_id)
                    if lemma and lemma.strip():
                        book_lemmas.append(lemma.strip())
                except Exception:
                    pass

        book_lemma_counts = Counter(book_lemmas)
        print(f"SUCCESS: Extracted {len(book_lemmas)} lemmas from {book_name} sample")
        print(f"SUCCESS: Unique lemmas: {len(book_lemma_counts)}")

        return book_lemma_counts

    except Exception as e:
        print(f"FAILED: {book_name} extraction error: {e}")
        return None

def step5_test_rare_logic(job_counts, other_counts):
    """Step 5: Test rare vocabulary logic with samples"""
    print("\nSTEP 5: Testing rare vocabulary logic")
    print("-" * 40)

    if not job_counts or not other_counts:
        print("FAILED: Missing data for rare logic test")
        return False

    # Combine counts to simulate total corpus
    all_counts = Counter()
    all_counts.update(job_counts)
    all_counts.update(other_counts)

    print(f"Combined corpus: {len(all_counts)} unique lemmas")

    # Test different thresholds
    thresholds = [1, 2, 5, 10]

    for threshold in thresholds:
        rare_count = 0
        rare_examples = []

        for lemma in job_counts:
            total_count = all_counts[lemma]
            job_count = job_counts[lemma]
            outside_job_count = total_count - job_count

            if outside_job_count < threshold:
                rare_count += 1
                if len(rare_examples) < 3:
                    rare_examples.append(f"{lemma} (Job:{job_count}, Outside:{outside_job_count})")

        print(f"Threshold <{threshold}: {rare_count} rare lemmas")
        if rare_examples:
            print(f"  Examples: {', '.join(rare_examples)}")

    return True

def run_step_by_step_debug():
    """Run complete step-by-step debugging"""
    print("ETCBC STEP-BY-STEP DEBUGGING")
    print("="*50)

    # Step 1: Connection
    A = step1_basic_connection()
    if not A:
        print("\nFAILED: Cannot connect to ETCBC")
        return

    # Step 2: Sample extraction
    if not step2_job_lemma_extraction(A):
        print("\nFAILED: Cannot extract sample lemmas")
        return

    # Step 3: Full Job extraction
    job_counts = step3_full_job_extraction(A)
    if not job_counts:
        print("\nFAILED: Cannot extract full Job lemmas")
        return

    # Step 4: Other book
    other_counts = step4_test_other_book(A)
    if not other_counts:
        print("\nFAILED: Cannot extract other book lemmas")
        return

    # Step 5: Logic test
    if not step5_test_rare_logic(job_counts, other_counts):
        print("\nFAILED: Rare vocabulary logic broken")
        return

    print("\nSUCCESS: All steps working!")
    print("The problem must be in the full implementation logic.")

if __name__ == "__main__":
    run_step_by_step_debug()