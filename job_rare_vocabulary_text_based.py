#!/usr/bin/env python3
"""
JOB RARE VOCABULARY ANALYSIS (TEXT-BASED APPROACH)

PURPOSE:
This script identifies which Old Testament books share the most rare vocabulary with Job
using the Hebrew text files we already have. While not as sophisticated as lemmatized
analysis, it provides meaningful insights into lexical relationships.

METHODOLOGY:
1. Parse Hebrew text files to extract words from each book
2. Normalize Hebrew text by removing most diacritics while preserving word forms
3. Count word frequencies across the entire Hebrew Bible
4. Identify Job's rare vocabulary (words appearing <10 times elsewhere)
5. Calculate overlap metrics for each book

TECHNICAL APPROACH:
- Uses our existing Hebrew text files from Westminster Leningrad Codex
- Normalizes Hebrew text similar to the bicola analysis approach
- Handles maqqeph-separated words as individual lexical units
- Provides both raw counts and normalized frequencies

OUTPUT:
Generates results/job_rare_vocabulary_text_based_results.txt with analysis results.
"""

import re
import os
from collections import Counter, defaultdict

# Hebrew text normalization (adapted from bicola analysis)
ETNACHTA = '\u0591'   # ֑
SOF_PASUQ = '\u05C3'  # ׃
MAQAF = '\u05BE'      # ־

# Remove most diacritics but keep structural markers
REMOVE = ''.join(chr(c) for c in list(range(0x0591,0x05BE)) + list(range(0x05BF,0x05C8)))
REMOVE = REMOVE.replace(ETNACHTA, '')
DIACRITICS_RE = re.compile(f"[{re.escape(REMOVE)}]")

def normalize_hebrew_word(word):
    """Normalize Hebrew word for lexical comparison."""
    # Remove most diacritics but keep basic structure
    normalized = DIACRITICS_RE.sub('', word)
    # Remove punctuation
    normalized = re.sub(r'[׃פס]', '', normalized)
    return normalized.strip()

def parse_hebrew_book(file_path):
    """Parse a Hebrew book file and extract normalized words."""
    words = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Process each line
        for line in content.split('\n'):
            # Remove Unicode directional marks
            clean_line = re.sub(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', line).strip()

            if not clean_line or 'xxxx' in clean_line:
                continue

            # Look for verse pattern: number ׃number hebrew_text
            match = re.search(r'(\d+)\s+׃(\d+)\s+(.+)', clean_line)
            if match:
                hebrew_text = match.group(3).strip()

                # Remove final punctuation
                hebrew_text = re.sub(r'[׃פס]\s*$', '', hebrew_text).strip()

                # Split by spaces and then by maqqeph
                word_groups = hebrew_text.split()
                for word_group in word_groups:
                    # Split by maqqeph to get individual words
                    maqqeph_parts = word_group.split('־')
                    for part in maqqeph_parts:
                        if part.strip() and any('\u0590' <= c <= '\u05FF' for c in part):
                            normalized_word = normalize_hebrew_word(part.strip())
                            if normalized_word:
                                words.append(normalized_word)

    except Exception as e:
        print(f"Error parsing {file_path}: {e}")

    return words

def get_all_hebrew_books():
    """Get list of all Hebrew book files."""
    tanakh_dir = "texts/tanakh"
    books = []

    try:
        for filename in os.listdir(tanakh_dir):
            if filename.endswith('.txt'):
                book_name = filename[:-4]  # Remove .txt extension
                file_path = os.path.join(tanakh_dir, filename)
                books.append((book_name, file_path))
    except Exception as e:
        print(f"Error listing Hebrew books: {e}")

    return books

def analyze_job_vocabulary_text():
    """Main analysis function using text-based approach."""
    print("Starting Job rare vocabulary analysis (text-based)...")

    # Get all Hebrew books
    print("Getting list of Hebrew books...")
    all_books = get_all_hebrew_books()
    print(f"Found {len(all_books)} Hebrew books")

    if not all_books:
        print("No Hebrew books found. Check directory structure.")
        return

    # Parse all books and count words
    print("Parsing all Hebrew books and counting words...")
    all_word_counts = Counter()
    book_words = {}

    for book_name, file_path in all_books:
        print(f"Processing {book_name}...")

        words = parse_hebrew_book(file_path)
        book_words[book_name] = words

        # Count words
        for word in words:
            all_word_counts[word] += 1

    print(f"Processed {len(all_word_counts)} unique words across all books")

    # Focus on Job
    if 'job' not in book_words:
        print("Job not found in book list. Available books:")
        for book_name, _ in all_books:
            print(f"  {book_name}")
        return

    job_words = book_words['job']
    print(f"Job contains {len(job_words)} word tokens")

    # Find Job's rare vocabulary
    print("Identifying Job's rare vocabulary...")
    job_word_counts = Counter(job_words)
    rare_job_vocab = []

    for word in job_word_counts:
        total_count = all_word_counts[word]
        job_count = job_word_counts[word]
        outside_job_count = total_count - job_count

        if outside_job_count < 10:  # Threshold for "rare"
            rare_job_vocab.append({
                'word': word,
                'job_count': job_count,
                'outside_job_count': outside_job_count,
                'total_count': total_count
            })

    print(f"Found {len(rare_job_vocab)} rare Job words")

    # Analyze overlap with other books
    print("Analyzing vocabulary overlap with other books...")
    rare_words = set(item['word'] for item in rare_job_vocab)
    book_overlap = {}

    for book_name, words in book_words.items():
        if book_name == 'job':  # Skip Job itself
            continue

        word_counts = Counter(words)
        overlap_count = 0
        overlap_words = []

        for word in rare_words:
            if word in word_counts:
                count = word_counts[word]
                overlap_count += count
                overlap_words.append((word, count))

        # Calculate metrics
        total_words = len(words)
        overlap_ratio = overlap_count / total_words * 1000 if total_words > 0 else 0

        book_overlap[book_name] = {
            'overlap_count': overlap_count,
            'total_words': total_words,
            'overlap_ratio': overlap_ratio,
            'unique_rare_words': len(overlap_words),
            'overlap_words': overlap_words
        }

    # Generate report
    generate_text_based_report(rare_job_vocab, book_overlap)

def generate_text_based_report(rare_job_vocab, book_overlap):
    """Generate analysis report."""
    output_file = "results/job_rare_vocabulary_text_based_results.txt"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("JOB RARE VOCABULARY ANALYSIS (TEXT-BASED)\n")
            f.write("="*55 + "\n\n")

            f.write("METHODOLOGY: Analysis based on normalized Hebrew word forms\n")
            f.write("from Westminster Leningrad Codex text files.\n")
            f.write("Words are normalized by removing most diacritics while\n")
            f.write("preserving basic consonantal structure.\n\n")

            # Summary
            f.write(f"Job's rare vocabulary: {len(rare_job_vocab)} words\n")
            f.write("(Words appearing <10 times outside Job)\n\n")

            # Top rare words
            f.write("TOP 20 RAREST JOB WORDS:\n")
            f.write("-" * 30 + "\n")
            rare_sorted = sorted(rare_job_vocab, key=lambda x: x['outside_job_count'])
            for i, item in enumerate(rare_sorted[:20], 1):
                f.write(f"{i:2d}. {item['word']:<25} "
                       f"(Job: {item['job_count']}, Elsewhere: {item['outside_job_count']})\n")
            f.write("\n")

            # Book rankings
            f.write("BOOKS BY RARE VOCABULARY OVERLAP\n")
            f.write("="*40 + "\n\n")

            # Sort by frequency (normalized)
            f.write("BY FREQUENCY (rare Job words per 1000 words):\n")
            f.write("-" * 40 + "\n")
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
            f.write("DETAILED ANALYSIS - TOP 5 BOOKS BY FREQUENCY\n")
            f.write("="*45 + "\n\n")

            for i, (book, data) in enumerate(books_by_ratio[:5], 1):
                f.write(f"{i}. {book.upper()}\n")
                f.write("-" * (len(book) + 3) + "\n")
                f.write(f"Overlap ratio: {data['overlap_ratio']:.2f} per 1000 words\n")
                f.write(f"Total rare Job words: {data['overlap_count']}\n")
                f.write(f"Unique rare words: {data['unique_rare_words']}\n")
                f.write(f"Book size: {data['total_words']} words\n\n")

                if data['overlap_words']:
                    f.write("Rare Job words found in this book:\n")
                    overlap_sorted = sorted(data['overlap_words'], key=lambda x: x[1], reverse=True)
                    for word, count in overlap_sorted[:15]:
                        f.write(f"  {word} ({count}x)\n")
                    if len(overlap_sorted) > 15:
                        f.write(f"  ... and {len(overlap_sorted) - 15} more\n")
                f.write("\n")

        print(f"Analysis complete! Results saved to {output_file}")

    except Exception as e:
        print(f"Error generating report: {e}")

if __name__ == "__main__":
    analyze_job_vocabulary_text()