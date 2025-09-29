#!/usr/bin/env python3
"""
JOB RARE VOCABULARY ANALYSIS (SIMPLIFIED)

PURPOSE:
Identifies which Old Testament books share the most rare vocabulary with Job.
Uses ETCBC BHSA dataset to find words distinctive to Job and analyze their
distribution across other biblical books.

METHODOLOGY:
1. Load ETCBC BHSA dataset with minimal feature set to avoid Unicode issues
2. Extract lexemes from Job and count their frequencies across all books
3. Identify Job's rare vocabulary (appearing <10 times elsewhere)
4. Calculate overlap metrics for each book

OUTPUT:
Generates job_vocabulary_simple_results.txt with analysis results.
"""

import sys
import os
from collections import Counter, defaultdict

# Set environment for Unicode handling
os.environ['PYTHONIOENCODING'] = 'utf-8'

def load_bhsa_simple():
    """Load BHSA dataset with minimal features to avoid console issues."""
    print("Loading ETCBC BHSA dataset (minimal approach)...")

    try:
        from tf.app import use

        # Load with only essential features and silent mode
        A = use('etcbc/bhsa', silent=True, load=['lex', 'book'])

        if A and hasattr(A, 'api'):
            print("Dataset loaded successfully!")
            return A
        else:
            print("Failed to load dataset")
            return None

    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def get_book_words_direct(A, book_name):
    """Get word nodes for a specific book using direct search."""
    try:
        # Search for words in the specified book
        words = A.search(f'book book={book_name}\n<< word')
        return words
    except Exception as e:
        print(f"Error searching for words in {book_name}: {e}")
        return []

def extract_lexemes_safe(A, words):
    """Safely extract lexemes from word nodes."""
    lexemes = []

    for word in words:
        try:
            # Get lexeme using the API
            lexeme = A.api.F.lex.v(word)
            if lexeme and lexeme.strip():
                lexemes.append(lexeme.strip())
        except Exception as e:
            # Skip problematic words silently
            continue

    return lexemes

def get_all_books(A):
    """Get list of all books in the dataset."""
    try:
        # Get book frequency list
        book_freq_list = A.api.F.book.freqList()
        books = [book for freq, book in book_freq_list if book]
        return books
    except Exception as e:
        print(f"Error getting book list: {e}")
        return []

def analyze_job_vocabulary():
    """Main analysis function."""
    print("Starting Job vocabulary analysis...")

    # Load dataset
    A = load_bhsa_simple()
    if not A:
        print("Failed to load dataset. Exiting.")
        return

    # Get Job's words (Job is called "Iob" in ETCBC)
    print("Extracting words from Job...")
    job_words = get_book_words_direct(A, 'Iob')
    print(f"Found {len(job_words)} word tokens in Job")

    if not job_words:
        print("No words found in Job. Check book name or search syntax.")
        return

    # Extract lexemes from Job
    print("Extracting lexemes from Job...")
    job_lexemes = extract_lexemes_safe(A, job_words)
    print(f"Extracted {len(job_lexemes)} lexemes from Job")

    if not job_lexemes:
        print("No lexemes extracted from Job. Check feature access.")
        return

    # Get all books
    print("Getting list of all books...")
    all_books = get_all_books(A)
    print(f"Found {len(all_books)} books in dataset")

    # Count lexemes across all books
    print("Counting lexemes across all books...")
    all_lexeme_counts = Counter()
    book_lexemes = {}

    for i, book in enumerate(all_books, 1):
        print(f"Processing {book} ({i}/{len(all_books)})...")

        try:
            # Get words for this book
            words = get_book_words_direct(A, book)

            # Extract lexemes
            lexemes = extract_lexemes_safe(A, words)
            book_lexemes[book] = lexemes

            # Count lexemes
            for lexeme in lexemes:
                all_lexeme_counts[lexeme] += 1

        except Exception as e:
            print(f"Error processing {book}: {e}")
            book_lexemes[book] = []

    print(f"Processed {len(all_lexeme_counts)} unique lexemes across all books")

    # Find Job's rare vocabulary
    print("Identifying Job's rare vocabulary...")
    job_lexeme_counts = Counter(job_lexemes)
    rare_job_vocab = []

    for lexeme in job_lexeme_counts:
        total_count = all_lexeme_counts[lexeme]
        job_count = job_lexeme_counts[lexeme]
        outside_job_count = total_count - job_count

        if outside_job_count < 10:  # Threshold for "rare"
            rare_job_vocab.append({
                'lexeme': lexeme,
                'job_count': job_count,
                'outside_job_count': outside_job_count,
                'total_count': total_count
            })

    print(f"Found {len(rare_job_vocab)} rare Job lexemes")

    # Analyze overlap with other books
    print("Analyzing vocabulary overlap...")
    rare_lexemes = set(item['lexeme'] for item in rare_job_vocab)
    book_overlap = {}

    for book, lexemes in book_lexemes.items():
        if book == 'Iob':  # Skip Job itself
            continue

        lexeme_counts = Counter(lexemes)
        overlap_count = 0
        overlap_words = []

        for lexeme in rare_lexemes:
            if lexeme in lexeme_counts:
                count = lexeme_counts[lexeme]
                overlap_count += count
                overlap_words.append((lexeme, count))

        # Calculate metrics
        total_words = len(lexemes)
        overlap_ratio = overlap_count / total_words * 1000 if total_words > 0 else 0

        book_overlap[book] = {
            'overlap_count': overlap_count,
            'total_words': total_words,
            'overlap_ratio': overlap_ratio,
            'unique_rare_words': len(overlap_words),
            'overlap_words': overlap_words
        }

    # Generate report
    generate_simple_report(rare_job_vocab, book_overlap)

def generate_simple_report(rare_job_vocab, book_overlap):
    """Generate a simple text report."""
    output_file = "job_vocabulary_simple_results.txt"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("JOB RARE VOCABULARY ANALYSIS\n")
            f.write("="*50 + "\n\n")

            # Summary
            f.write(f"Job's rare vocabulary: {len(rare_job_vocab)} lexemes\n")
            f.write("(Lexemes appearing <10 times outside Job)\n\n")

            # Top rare lexemes
            f.write("TOP 20 RAREST JOB LEXEMES:\n")
            f.write("-" * 30 + "\n")
            rare_sorted = sorted(rare_job_vocab, key=lambda x: x['outside_job_count'])
            for i, item in enumerate(rare_sorted[:20], 1):
                f.write(f"{i:2d}. {item['lexeme']:<20} "
                       f"(Job: {item['job_count']}, Elsewhere: {item['outside_job_count']})\n")
            f.write("\n")

            # Book rankings
            f.write("BOOKS BY RARE VOCABULARY OVERLAP\n")
            f.write("="*40 + "\n\n")

            # Sort by frequency (normalized)
            f.write("BY FREQUENCY (per 1000 words):\n")
            f.write("-" * 30 + "\n")
            books_by_ratio = sorted(book_overlap.items(),
                                   key=lambda x: x[1]['overlap_ratio'], reverse=True)

            for i, (book, data) in enumerate(books_by_ratio[:15], 1):
                f.write(f"{i:2d}. {book:<20} {data['overlap_ratio']:6.2f} "
                       f"({data['overlap_count']} total, {data['unique_rare_words']} unique)\n")

            f.write("\n")

            # Sort by absolute count
            f.write("BY ABSOLUTE COUNT:\n")
            f.write("-" * 20 + "\n")
            books_by_count = sorted(book_overlap.items(),
                                   key=lambda x: x[1]['overlap_count'], reverse=True)

            for i, (book, data) in enumerate(books_by_count[:15], 1):
                f.write(f"{i:2d}. {book:<20} {data['overlap_count']:3d} total "
                       f"({data['overlap_ratio']:5.2f} per 1000)\n")

            f.write("\n")

            # Detailed analysis for top books
            f.write("DETAILED ANALYSIS - TOP 5 BOOKS\n")
            f.write("="*35 + "\n\n")

            for i, (book, data) in enumerate(books_by_ratio[:5], 1):
                f.write(f"{i}. {book}\n")
                f.write("-" * len(book) + "\n")
                f.write(f"Overlap ratio: {data['overlap_ratio']:.2f} per 1000 words\n")
                f.write(f"Total rare Job words: {data['overlap_count']}\n")
                f.write(f"Unique rare lexemes: {data['unique_rare_words']}\n")
                f.write(f"Book size: {data['total_words']} words\n\n")

                if data['overlap_words']:
                    f.write("Top rare Job lexemes in this book:\n")
                    overlap_sorted = sorted(data['overlap_words'], key=lambda x: x[1], reverse=True)
                    for lexeme, count in overlap_sorted[:10]:
                        f.write(f"  {lexeme} ({count}x)\n")
                    if len(overlap_sorted) > 10:
                        f.write(f"  ... and {len(overlap_sorted) - 10} more\n")
                f.write("\n")

        print(f"Analysis complete! Results saved to {output_file}")

    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    analyze_job_vocabulary()