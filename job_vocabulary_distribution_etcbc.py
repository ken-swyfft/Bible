#!/usr/bin/env python3
"""
JOB VOCABULARY DISTRIBUTION ANALYSIS (ETCBC BHSA)

PURPOSE:
Analyze the distribution of Job's vocabulary across other biblical books using
proper morphological data. Instead of focusing only on "rare" vocabulary,
this provides a comprehensive view of lexical relationships.

METHODOLOGY:
1. Extract all lemmas from Job and other books using ETCBC BHSA
2. Calculate Job's distinctive vocabulary (appearing less frequently elsewhere)
3. Analyze vocabulary overlap patterns across books
4. Show distribution gradients rather than just rare/common binary

OUTPUT:
Generates job_vocabulary_distribution_etcbc_results.txt with comprehensive analysis.
"""

import os
import sys
from collections import Counter, defaultdict

# Critical: Set environment for UTF-8 handling
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

class SafeUnicodeHandler:
    """Handle Unicode output safely on Windows console"""
    def __init__(self):
        self.original_stdout = sys.stdout

    def safe_print(self, text):
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = str(text).encode('ascii', errors='replace').decode('ascii')
            print(safe_text)

def load_etcbc_dataset():
    """Load ETCBC BHSA dataset with proper error handling."""
    handler = SafeUnicodeHandler()
    handler.safe_print("Loading ETCBC BHSA dataset...")

    try:
        from tf.app import use
        A = use('etcbc/bhsa', silent=True)

        if A and hasattr(A, 'api'):
            handler.safe_print("Dataset loaded successfully!")
            return A, handler
        else:
            handler.safe_print("Failed to load dataset")
            return None, handler

    except Exception as e:
        handler.safe_print(f"Error loading dataset: {e}")
        return None, handler

def extract_book_lemmas_safe(A, book_name, handler):
    """Extract lemmas from a specific book using proper morphological access."""
    lemmas = []

    try:
        words = A.search(f'book book={book_name}\n<< word')

        for word_tuple in words:
            if len(word_tuple) >= 2:
                word_id = word_tuple[1]
                try:
                    lemma = A.api.F.lex.v(word_id)
                    if lemma and lemma.strip():
                        lemmas.append(lemma.strip())
                except Exception:
                    pass

    except Exception as e:
        handler.safe_print(f"Error extracting lemmas from {book_name}: {e}")

    return lemmas

def analyze_job_vocabulary_distribution():
    """Analyze Job's vocabulary distribution across all books."""
    # Load dataset
    A, handler = load_etcbc_dataset()
    if not A:
        return

    # Get all books
    handler.safe_print("Getting list of all books...")
    book_nodes = A.search('book')
    all_books = []

    for book_tuple in book_nodes:
        book_id = book_tuple[0]
        book_name = A.api.F.book.v(book_id)
        if book_name and book_name.strip():
            all_books.append(book_name.strip())

    handler.safe_print(f"Found {len(all_books)} books")

    if 'Iob' not in all_books:
        handler.safe_print("Job (Iob) not found!")
        return

    # Extract Job's lemmas
    handler.safe_print("Extracting lemmas from Job...")
    job_lemmas = extract_book_lemmas_safe(A, 'Iob', handler)
    job_lemma_counts = Counter(job_lemmas)

    handler.safe_print(f"Job: {len(job_lemmas)} tokens, {len(job_lemma_counts)} unique lemmas")

    # Process all other books
    handler.safe_print("Processing all other books...")
    all_lemma_counts = Counter()
    book_lemmas = {}

    for i, book in enumerate(all_books, 1):
        handler.safe_print(f"Processing {book} ({i}/{len(all_books)})...")

        lemmas = extract_book_lemmas_safe(A, book, handler)
        book_lemmas[book] = Counter(lemmas)

        # Add to total counts
        for lemma in lemmas:
            all_lemma_counts[lemma] += 1

    # Analyze Job's vocabulary distribution
    handler.safe_print("Analyzing vocabulary distribution...")

    # Create distribution categories
    job_vocab_analysis = {}

    for lemma, job_count in job_lemma_counts.items():
        total_count = all_lemma_counts[lemma]
        outside_job_count = total_count - job_count

        # Calculate frequency ratio
        job_frequency = job_count / len(job_lemmas)
        total_frequency = total_count / sum(all_lemma_counts.values())

        # Job distinctiveness score (higher = more distinctive to Job)
        distinctiveness = job_frequency / total_frequency if total_frequency > 0 else 0

        job_vocab_analysis[lemma] = {
            'job_count': job_count,
            'total_count': total_count,
            'outside_job_count': outside_job_count,
            'distinctiveness': distinctiveness,
            'job_frequency': job_frequency,
            'total_frequency': total_frequency
        }

    # Analyze book overlaps with different Job vocabulary tiers
    handler.safe_print("Analyzing book overlaps...")

    # Define vocabulary tiers based on distinctiveness
    highly_distinctive = {k: v for k, v in job_vocab_analysis.items() if v['distinctiveness'] > 2.0}
    moderately_distinctive = {k: v for k, v in job_vocab_analysis.items() if 1.0 < v['distinctiveness'] <= 2.0}
    common_vocabulary = {k: v for k, v in job_vocab_analysis.items() if v['distinctiveness'] <= 1.0}

    handler.safe_print(f"Highly distinctive: {len(highly_distinctive)} lemmas")
    handler.safe_print(f"Moderately distinctive: {len(moderately_distinctive)} lemmas")
    handler.safe_print(f"Common vocabulary: {len(common_vocabulary)} lemmas")

    # Calculate overlaps for each book
    book_overlaps = {}

    for book, book_lemma_counts in book_lemmas.items():
        if book == 'Iob':
            continue

        # Calculate overlaps for each tier
        highly_dist_overlap = sum(book_lemma_counts[lemma] for lemma in highly_distinctive if lemma in book_lemma_counts)
        mod_dist_overlap = sum(book_lemma_counts[lemma] for lemma in moderately_distinctive if lemma in book_lemma_counts)
        common_overlap = sum(book_lemma_counts[lemma] for lemma in common_vocabulary if lemma in book_lemma_counts)

        total_words = sum(book_lemma_counts.values())

        book_overlaps[book] = {
            'highly_distinctive': highly_dist_overlap,
            'moderately_distinctive': mod_dist_overlap,
            'common_vocabulary': common_overlap,
            'total_words': total_words,
            'highly_dist_ratio': highly_dist_overlap / total_words * 1000 if total_words > 0 else 0,
            'mod_dist_ratio': mod_dist_overlap / total_words * 1000 if total_words > 0 else 0,
            'common_ratio': common_overlap / total_words * 1000 if total_words > 0 else 0
        }

    # Generate comprehensive report
    generate_distribution_report(
        job_vocab_analysis,
        highly_distinctive,
        moderately_distinctive,
        common_vocabulary,
        book_overlaps,
        handler
    )

def generate_distribution_report(job_vocab_analysis, highly_distinctive, moderately_distinctive,
                               common_vocabulary, book_overlaps, handler):
    """Generate comprehensive vocabulary distribution report."""
    output_file = "job_vocabulary_distribution_etcbc_results.txt"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("JOB VOCABULARY DISTRIBUTION ANALYSIS (ETCBC BHSA)\n")
            f.write("="*65 + "\n\n")

            f.write("METHODOLOGY: Comprehensive morphological analysis using ETCBC BHSA.\n")
            f.write("Analyzes vocabulary distribution rather than just rare/common binary.\n")
            f.write("Uses distinctiveness scores to identify Job's characteristic vocabulary.\n\n")

            # Vocabulary distribution summary
            f.write("JOB VOCABULARY DISTRIBUTION:\n")
            f.write("-" * 35 + "\n")
            f.write(f"Highly distinctive lemmas: {len(highly_distinctive)} (distinctiveness > 2.0)\n")
            f.write(f"Moderately distinctive lemmas: {len(moderately_distinctive)} (1.0-2.0)\n")
            f.write(f"Common vocabulary lemmas: {len(common_vocabulary)} (≤ 1.0)\n\n")

            # Top distinctive vocabulary
            f.write("TOP 20 MOST DISTINCTIVE JOB LEMMAS:\n")
            f.write("-" * 40 + "\n")
            sorted_by_distinctiveness = sorted(job_vocab_analysis.items(),
                                             key=lambda x: x[1]['distinctiveness'], reverse=True)

            for i, (lemma, data) in enumerate(sorted_by_distinctiveness[:20], 1):
                f.write(f"{i:2d}. {lemma:<20} "
                       f"(Distinct: {data['distinctiveness']:.2f}, Job: {data['job_count']}, "
                       f"Outside: {data['outside_job_count']})\n")
            f.write("\n")

            # Book overlap analysis
            f.write("BOOKS BY DISTINCTIVE VOCABULARY OVERLAP:\n")
            f.write("="*45 + "\n\n")

            # Sort by highly distinctive vocabulary overlap
            f.write("BY HIGHLY DISTINCTIVE JOB VOCABULARY (per 1000 words):\n")
            f.write("-" * 50 + "\n")
            books_by_highly_dist = sorted(book_overlaps.items(),
                                        key=lambda x: x[1]['highly_dist_ratio'], reverse=True)

            for i, (book, data) in enumerate(books_by_highly_dist[:15], 1):
                f.write(f"{i:2d}. {book:<20} {data['highly_dist_ratio']:6.2f} "
                       f"({data['highly_distinctive']} tokens)\n")

            f.write("\n")

            # Sort by moderately distinctive vocabulary
            f.write("BY MODERATELY DISTINCTIVE VOCABULARY (per 1000 words):\n")
            f.write("-" * 50 + "\n")
            books_by_mod_dist = sorted(book_overlaps.items(),
                                     key=lambda x: x[1]['mod_dist_ratio'], reverse=True)

            for i, (book, data) in enumerate(books_by_mod_dist[:15], 1):
                f.write(f"{i:2d}. {book:<20} {data['mod_dist_ratio']:6.2f} "
                       f"({data['moderately_distinctive']} tokens)\n")

            f.write("\n")

            # Detailed analysis for top books
            f.write("DETAILED ANALYSIS - TOP 5 BOOKS BY DISTINCTIVE VOCABULARY\n")
            f.write("="*60 + "\n\n")

            for i, (book, data) in enumerate(books_by_highly_dist[:5], 1):
                f.write(f"{i}. {book}\n")
                f.write("-" * (len(book) + 3) + "\n")
                f.write(f"Highly distinctive overlap: {data['highly_dist_ratio']:.2f} per 1000\n")
                f.write(f"Moderately distinctive overlap: {data['mod_dist_ratio']:.2f} per 1000\n")
                f.write(f"Common vocabulary overlap: {data['common_ratio']:.2f} per 1000\n")
                f.write(f"Book size: {data['total_words']} words\n\n")

            # Methodological notes
            f.write("METHODOLOGICAL NOTES:\n")
            f.write("="*22 + "\n")
            f.write("- Distinctiveness = (Job frequency) / (Overall frequency)\n")
            f.write("- Higher distinctiveness = more characteristic of Job\n")
            f.write("- Lemmas represent morphologically normalized forms\n")
            f.write("- Analysis reveals lexical relationships beyond simple frequency\n")
            f.write("- ETCBC annotations ensure linguistic accuracy\n")

        handler.safe_print(f"Comprehensive analysis complete! Results saved to {output_file}")

    except Exception as e:
        handler.safe_print(f"Error generating report: {e}")

if __name__ == "__main__":
    analyze_job_vocabulary_distribution()