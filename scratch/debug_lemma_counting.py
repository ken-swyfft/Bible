#!/usr/bin/env python3
"""Debug the lemma counting logic"""

import os
from collections import Counter

os.environ['PYTHONIOENCODING'] = 'utf-8'

from tf.app import use

A = use('etcbc/bhsa', silent=True)

if A:
    print("Testing lemma counting logic...")

    # Get Job lemmas
    job_words = A.search('book book=Iob\n<< word')
    job_lemmas = []

    for word_tuple in job_words[:1000]:  # Test first 1000 words
        if len(word_tuple) >= 2:
            word_id = word_tuple[1]
            try:
                lemma = A.api.F.lex.v(word_id)
                if lemma and lemma.strip():
                    job_lemmas.append(lemma.strip())
            except Exception:
                pass

    print(f"Sample Job lemmas extracted: {len(job_lemmas)}")
    job_lemma_counts = Counter(job_lemmas)

    # Show most common Job lemmas
    print("Most common Job lemmas:")
    for lemma, count in job_lemma_counts.most_common(10):
        print(f"  {lemma}: {count}")

    # Test counting across other books
    print("\nTesting Genesis lemma extraction...")
    genesis_words = A.search('book book=Genesis\n<< word')
    genesis_lemmas = []

    for word_tuple in genesis_words[:1000]:  # Test sample
        if len(word_tuple) >= 2:
            word_id = word_tuple[1]
            try:
                lemma = A.api.F.lex.v(word_id)
                if lemma and lemma.strip():
                    genesis_lemmas.append(lemma.strip())
            except Exception:
                pass

    print(f"Genesis lemmas extracted: {len(genesis_lemmas)}")
    genesis_lemma_counts = Counter(genesis_lemmas)

    # Check overlap
    print("\nChecking overlap between Job and Genesis samples:")
    job_set = set(job_lemma_counts.keys())
    genesis_set = set(genesis_lemma_counts.keys())
    overlap = job_set.intersection(genesis_set)

    print(f"Job unique lemmas: {len(job_set)}")
    print(f"Genesis unique lemmas: {len(genesis_set)}")
    print(f"Overlapping lemmas: {len(overlap)}")

    print("Sample overlapping lemmas:")
    for lemma in list(overlap)[:10]:
        print(f"  {lemma}: Job={job_lemma_counts[lemma]}, Genesis={genesis_lemma_counts[lemma]}")

    # Test rare vocabulary logic
    print("\nTesting rare vocabulary identification...")
    all_lemma_counts = Counter()
    all_lemma_counts.update(job_lemma_counts)
    all_lemma_counts.update(genesis_lemma_counts)

    rare_count = 0
    for lemma in job_lemma_counts:
        total_count = all_lemma_counts[lemma]
        job_count = job_lemma_counts[lemma]
        outside_job_count = total_count - job_count

        if outside_job_count < 10:
            rare_count += 1
            if rare_count <= 5:  # Show first 5
                print(f"  Rare: {lemma} (Job: {job_count}, Outside: {outside_job_count})")

    print(f"Total rare lemmas found: {rare_count}")

    if rare_count == 0:
        print("DEBUG: No rare lemmas found. Checking threshold...")
        # Try different thresholds
        for threshold in [5, 3, 1]:
            rare_at_threshold = 0
            for lemma in job_lemma_counts:
                total_count = all_lemma_counts[lemma]
                job_count = job_lemma_counts[lemma]
                outside_job_count = total_count - job_count

                if outside_job_count < threshold:
                    rare_at_threshold += 1

            print(f"  Rare lemmas at threshold {threshold}: {rare_at_threshold}")