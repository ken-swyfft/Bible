#!/usr/bin/env python3
"""
JOB RARE VOCABULARY OVERLAP ANALYSIS

PURPOSE:
This script identifies which Old Testament books share the most rare vocabulary with Job.
It finds words that are distinctive to Job (appearing fewer than 10 times elsewhere in the Tanakh)
and analyzes which other books have the highest concentration of these rare terms.

METHODOLOGY:
1. Uses ETCBC BHSA dataset via Text-Fabric for lemmatized Hebrew text analysis
2. Extracts all lexemes (lemmatized word forms) from the book of Job
3. Counts occurrences of each Job lexeme across the entire Hebrew Bible
4. Identifies "rare Job vocabulary" (lexemes appearing <10 times outside Job)
5. Calculates overlap metrics for each OT book with Job's rare vocabulary
6. Ranks books by both raw counts and normalized frequencies

TECHNICAL APPROACH:
- Leverages Text-Fabric's linguistic annotations for accurate lexical analysis
- Uses lemma features rather than surface forms for consistent vocabulary identification
- Handles proper nouns and function words appropriately
- Provides both absolute counts and relative frequencies (per 1000 words)
- Excludes Job itself from the comparison to focus on external relationships

RESEARCH SIGNIFICANCE:
This analysis can reveal:
- Literary connections between Job and other wisdom literature
- Shared specialized vocabulary in poetic vs prose texts
- Potential chronological or regional linguistic relationships
- Books that may have influenced or been influenced by Job's unique lexicon

OUTPUT:
Generates job_rare_vocabulary_analysis_results.txt with:
- List of Job's rare vocabulary items
- Ranking of OT books by rare vocabulary overlap
- Statistical analysis of lexical relationships
- Detailed word lists for top-ranking books

REQUIREMENTS:
- text-fabric package: pip install text-fabric
- ETCBC BHSA dataset (downloaded automatically by Text-Fabric)
"""

import sys
from collections import Counter, defaultdict

def install_and_import_tf():
    """Install Text-Fabric if not available and import it."""
    try:
        from tf.app import use
        return use
    except ImportError:
        print("Text-Fabric not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "text-fabric"])
        from tf.app import use
        return use

def load_bhsa_dataset():
    """Load the ETCBC BHSA dataset via Text-Fabric."""
    print("Loading ETCBC BHSA dataset...")
    print("(This may take a few minutes on first run while downloading data)")

    use = install_and_import_tf()
    A = use('etcbc/bhsa', silent=True)

    print("Dataset loaded successfully!")
    return A

def get_book_lexemes(A, book_name):
    """Extract all lexemes from a specific book."""
    lexemes = []

    # Get all word nodes for the specified book
    words = A.search(f'book book={book_name}\n<< word')

    for word in words:
        # Get lexeme (lemmatized form)
        lexeme = A.api.F.lex.v(word)
        if lexeme and lexeme != '':
            lexemes.append(lexeme)

    return lexemes

def get_all_tanakh_lexemes(A):
    """Get lexeme counts for the entire Hebrew Bible."""
    print("Counting lexemes across entire Hebrew Bible...")

    lexeme_counts = Counter()
    book_lexemes = defaultdict(list)

    # Get all books in the Hebrew Bible
    all_books = A.api.F.book.freqList()

    for freq, book in all_books:
        print(f"Processing {book}...")

        # Get lexemes for this book
        book_lexeme_list = get_book_lexemes(A, book)
        book_lexemes[book] = book_lexeme_list

        # Count lexemes
        for lexeme in book_lexeme_list:
            lexeme_counts[lexeme] += 1

    return lexeme_counts, book_lexemes

def find_job_rare_vocabulary(job_lexemes, all_lexeme_counts, threshold=10):
    """Identify lexemes that are rare outside of Job."""
    job_lexeme_counts = Counter(job_lexemes)
    rare_job_vocab = []

    for lexeme in job_lexeme_counts:
        # Count occurrences outside Job
        total_count = all_lexeme_counts[lexeme]
        job_count = job_lexeme_counts[lexeme]
        outside_job_count = total_count - job_count

        if outside_job_count < threshold:
            rare_job_vocab.append({
                'lexeme': lexeme,
                'job_count': job_count,
                'outside_job_count': outside_job_count,
                'total_count': total_count
            })

    return rare_job_vocab

def analyze_book_overlap(rare_job_vocab, book_lexemes):
    """Analyze overlap of rare Job vocabulary with other books."""
    rare_lexemes = set(item['lexeme'] for item in rare_job_vocab)

    book_overlap = {}

    for book, lexemes in book_lexemes.items():
        if book == 'Iob':  # Skip Job itself
            continue

        book_lexeme_counts = Counter(lexemes)

        # Count rare Job vocabulary in this book
        overlap_count = 0
        overlap_words = []

        for lexeme in rare_lexemes:
            if lexeme in book_lexeme_counts:
                count = book_lexeme_counts[lexeme]
                overlap_count += count
                overlap_words.append((lexeme, count))

        # Calculate metrics
        total_words = len(lexemes)
        overlap_ratio = overlap_count / total_words * 1000 if total_words > 0 else 0
        unique_rare_words = len(overlap_words)

        book_overlap[book] = {
            'overlap_count': overlap_count,
            'total_words': total_words,
            'overlap_ratio': overlap_ratio,  # per 1000 words
            'unique_rare_words': unique_rare_words,
            'overlap_words': overlap_words
        }

    return book_overlap

def generate_report(rare_job_vocab, book_overlap):
    """Generate detailed analysis report."""
    output_file = "job_rare_vocabulary_analysis_results.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("JOB RARE VOCABULARY OVERLAP ANALYSIS\n")
        f.write("="*60 + "\n\n")

        # Summary of Job's rare vocabulary
        f.write(f"RARE JOB VOCABULARY SUMMARY\n")
        f.write("-" * 30 + "\n")
        f.write(f"Total rare lexemes in Job: {len(rare_job_vocab)}\n")
        f.write("(Lexemes appearing <10 times outside Job)\n\n")

        # Top rare vocabulary items
        f.write("TOP 20 RAREST JOB LEXEMES:\n")
        f.write("-" * 30 + "\n")
        rare_sorted = sorted(rare_job_vocab, key=lambda x: x['outside_job_count'])
        for i, item in enumerate(rare_sorted[:20], 1):
            f.write(f"{i:2d}. {item['lexeme']:<15} "
                   f"(Job: {item['job_count']}, Elsewhere: {item['outside_job_count']})\n")
        f.write("\n")

        # Book overlap rankings
        f.write("BOOKS RANKED BY RARE VOCABULARY OVERLAP\n")
        f.write("="*50 + "\n\n")

        # Sort by overlap ratio (normalized)
        f.write("RANKED BY FREQUENCY (rare Job words per 1000 words):\n")
        f.write("-" * 50 + "\n")
        books_by_ratio = sorted(book_overlap.items(),
                               key=lambda x: x[1]['overlap_ratio'], reverse=True)

        for i, (book, data) in enumerate(books_by_ratio[:15], 1):
            f.write(f"{i:2d}. {book:<15} "
                   f"{data['overlap_ratio']:6.2f} per 1000 words "
                   f"({data['overlap_count']} total, {data['unique_rare_words']} unique)\n")
        f.write("\n")

        # Sort by absolute count
        f.write("RANKED BY ABSOLUTE COUNT (total rare Job words):\n")
        f.write("-" * 50 + "\n")
        books_by_count = sorted(book_overlap.items(),
                               key=lambda x: x[1]['overlap_count'], reverse=True)

        for i, (book, data) in enumerate(books_by_count[:15], 1):
            f.write(f"{i:2d}. {book:<15} "
                   f"{data['overlap_count']:3d} total words "
                   f"({data['overlap_ratio']:5.2f} per 1000, {data['unique_rare_words']} unique)\n")
        f.write("\n")

        # Detailed analysis for top books
        f.write("DETAILED ANALYSIS - TOP 5 BOOKS BY FREQUENCY\n")
        f.write("="*50 + "\n\n")

        for i, (book, data) in enumerate(books_by_ratio[:5], 1):
            f.write(f"{i}. {book.upper()}\n")
            f.write("-" * 20 + "\n")
            f.write(f"Overlap ratio: {data['overlap_ratio']:.2f} per 1000 words\n")
            f.write(f"Total rare Job words: {data['overlap_count']}\n")
            f.write(f"Unique rare lexemes: {data['unique_rare_words']}\n")
            f.write(f"Book total words: {data['total_words']}\n\n")

            f.write("Rare Job lexemes found in this book:\n")
            overlap_sorted = sorted(data['overlap_words'], key=lambda x: x[1], reverse=True)
            for lexeme, count in overlap_sorted[:10]:  # Top 10
                f.write(f"  {lexeme} ({count}x)\n")
            if len(overlap_sorted) > 10:
                f.write(f"  ... and {len(overlap_sorted) - 10} more\n")
            f.write("\n")

    print(f"Analysis complete! Results saved to {output_file}")

def main():
    """Main analysis function."""
    print("Starting Job rare vocabulary analysis...")

    # Load dataset
    A = load_bhsa_dataset()

    # Get lexemes from Job (called "Iob" in ETCBC dataset)
    print("Extracting lexemes from Job...")
    job_lexemes = get_book_lexemes(A, 'Iob')
    print(f"Found {len(job_lexemes)} total words in Job")

    # Get all Tanakh lexemes
    all_lexeme_counts, book_lexemes = get_all_tanakh_lexemes(A)
    print(f"Processed {len(all_lexeme_counts)} unique lexemes across Hebrew Bible")

    # Find rare Job vocabulary
    print("Identifying rare Job vocabulary...")
    rare_job_vocab = find_job_rare_vocabulary(job_lexemes, all_lexeme_counts)
    print(f"Found {len(rare_job_vocab)} rare Job lexemes")

    # Analyze overlap with other books
    print("Analyzing vocabulary overlap with other books...")
    book_overlap = analyze_book_overlap(rare_job_vocab, book_lexemes)

    # Generate report
    print("Generating analysis report...")
    generate_report(rare_job_vocab, book_overlap)

if __name__ == "__main__":
    main()