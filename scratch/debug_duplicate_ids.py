#!/usr/bin/env python3
"""
Check if search queries are returning duplicate word IDs
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

    print("\n" + "="*70)
    print("CHECKING FOR DUPLICATE WORD IDs IN SEARCH RESULTS")
    print("="*70)

    # Test with Genesis
    print("\nTesting Genesis...")
    words = A.search('book book=Genesis\n<< word')
    print(f"Total search results: {len(words)}")

    # Extract word IDs
    word_ids = []
    for word_tuple in words:
        if len(word_tuple) >= 2:
            word_id = word_tuple[1]
            word_ids.append(word_id)

    print(f"Total word IDs extracted: {len(word_ids)}")
    print(f"Unique word IDs: {len(set(word_ids))}")

    if len(word_ids) != len(set(word_ids)):
        print("\n*** DUPLICATES DETECTED! ***")
        id_counts = Counter(word_ids)
        duplicates = [(wid, count) for wid, count in id_counts.items() if count > 1]
        print(f"Number of word IDs appearing multiple times: {len(duplicates)}")

        print("\nFirst 10 duplicate IDs:")
        for wid, count in duplicates[:10]:
            lemma = A.api.F.lex.v(wid)
            print(f"  Word ID {wid}: appears {count} times, lemma='{lemma}'")

        # Analyze the pattern
        dup_count_dist = Counter([count for _, count in duplicates])
        print("\nDuplication pattern:")
        for count, freq in sorted(dup_count_dist.items()):
            print(f"  {freq} word IDs appear {count} times each")

    else:
        print("\nNo duplicates found - search results are clean")

    # Test with Job specifically
    print("\n" + "="*70)
    print("TESTING JOB:")
    print("="*70)

    words = A.search('book book=Iob\n<< word')
    print(f"Total search results: {len(words)}")

    word_ids = []
    for word_tuple in words:
        if len(word_tuple) >= 2:
            word_id = word_tuple[1]
            word_ids.append(word_id)

    print(f"Total word IDs extracted: {len(word_ids)}")
    print(f"Unique word IDs: {len(set(word_ids))}")

    if len(word_ids) != len(set(word_ids)):
        print("\n*** DUPLICATES DETECTED IN JOB! ***")
        id_counts = Counter(word_ids)
        duplicates = [(wid, count) for wid, count in id_counts.items() if count > 1]
        print(f"Number of word IDs appearing multiple times: {len(duplicates)}")
    else:
        print("\nNo duplicates in Job - search results are clean")

    # Alternative: Try a different search method
    print("\n" + "="*70)
    print("TESTING ALTERNATIVE SEARCH METHOD:")
    print("="*70)

    print("\nMethod 1: Using << relation")
    words1 = A.search('book book=Genesis\n<< word')
    print(f"Results: {len(words1)}")

    print("\nMethod 2: Direct book query")
    # Try getting book node first
    book_results = A.search('book book=Genesis')
    if book_results:
        print(f"Book results: {len(book_results)}")
        book_node = book_results[0][0] if isinstance(book_results[0], tuple) else book_results[0]
        print(f"Book node ID: {book_node}")

        # Get words using L.d (downward edges)
        if hasattr(A.api, 'L'):
            word_nodes = list(A.api.L.d(book_node, otype='word'))
            print(f"Words via L.d: {len(word_nodes)}")
            print(f"Unique: {len(set(word_nodes))}")

if __name__ == "__main__":
    main()