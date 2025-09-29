#!/usr/bin/env python3
"""
Simple diagnosis: What's actually in the lemma data?
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

    # Get a few sample verses from Job and show all lemma data
    print("\nExamining first verse of Job in detail...")
    print("="*70)

    # Get verse 1:1
    verses = A.search('book book=Iob\nchapter chapter=1\nverse verse=1')
    print(f"Found {len(verses)} matches for Job 1:1")

    if verses:
        verse_tuple = verses[0]
        print(f"Verse tuple: {verse_tuple}")

        # Get the verse node
        if len(verse_tuple) >= 3:
            verse_node = verse_tuple[2]
            print(f"Verse node ID: {verse_node}")

            # Get words in this verse
            words = A.search(f'book book=Iob\nchapter chapter=1\nverse verse=1\n<< word')
            print(f"\nWords in Job 1:1: {len(words)} results")

            print("\nFirst 10 words with their lemmas:")
            for i, word_tuple in enumerate(words[:10], 1):
                print(f"\n  Word {i}:")
                print(f"    Tuple: {word_tuple}")
                if len(word_tuple) >= 2:
                    word_id = word_tuple[1]
                    print(f"    Word ID: {word_id}")

                    # Get various features
                    lex = A.api.F.lex.v(word_id)
                    voc_lex = A.api.F.voc_lex_utf8.v(word_id)
                    g_word = A.api.F.g_word_utf8.v(word_id)

                    print(f"    lex (lemma): '{lex}'")
                    print(f"    voc_lex_utf8: '{voc_lex}'")
                    print(f"    g_word_utf8: '{g_word}'")

    # Now show Job lemma frequency distribution
    print("\n" + "="*70)
    print("JOB LEMMA FREQUENCY DISTRIBUTION:")
    print("="*70)

    job_words = A.search('book book=Iob\n<< word')
    job_lemmas = []
    for word_tuple in job_words:
        if len(word_tuple) >= 2:
            word_id = word_tuple[1]
            lemma = A.api.F.lex.v(word_id)
            if lemma and lemma.strip():
                job_lemmas.append(lemma.strip())

    job_lemma_counts = Counter(job_lemmas)
    print(f"\nTotal tokens in Job: {len(job_lemmas)}")
    print(f"Unique lemmas in Job: {len(job_lemma_counts)}")

    # Show distribution
    freq_dist = Counter()
    for lemma, count in job_lemma_counts.items():
        freq_dist[count] += 1

    print("\nFrequency distribution (how many lemmas appear N times):")
    for freq in sorted(freq_dist.keys())[:20]:
        print(f"  Appearing {freq:3d} times: {freq_dist[freq]:4d} lemmas")

    # Show most common lemmas
    print("\nTop 20 most frequent lemmas in Job:")
    for i, (lemma, count) in enumerate(job_lemma_counts.most_common(20), 1):
        print(f"  {i:2d}. {lemma:<20} {count:4d} times")

    # Show some rare lemmas
    print("\nSample of lemmas appearing exactly once in Job (first 20):")
    hapax = [lemma for lemma, count in job_lemma_counts.items() if count == 1]
    for i, lemma in enumerate(hapax[:20], 1):
        print(f"  {i:2d}. {lemma}")

if __name__ == "__main__":
    main()