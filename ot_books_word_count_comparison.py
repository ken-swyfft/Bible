#!/usr/bin/env python3
"""
OLD TESTAMENT BOOKS WORD COUNT COMPARISON

PURPOSE:
Compares total word counts between Hebrew text and English translation (NASB) for all
39 books of the Old Testament. Identifies which books exhibit the most/least Hebrew
conciseness relative to English.

METHODOLOGY:
1. Parses all 39 OT books from Westminster Leningrad Codex (Hebrew)
2. Parses all 39 OT books from NASB (English)
3. Counts total words per book using linguistically appropriate methods:
   - Hebrew: Treats maqqeph (־) separated words as individual words
   - Hebrew: Deduplicates ketiv/qere variants (keeps qere, removes ketiv)
   - English: Uses word boundary regex to handle punctuation properly
4. Calculates Hebrew/English ratios for each book
5. Sorts books by ratio from lowest (most concise Hebrew) to highest

TECHNICAL APPROACH:
- Reuses word counting logic from proverbs_analyze_word_ratios.py
- Handles Unicode directional marks in Hebrew text
- Deduplicates ketiv/qere: removes *ketiv, keeps **qere (pattern: *וצפן **יִצְפֹּ֣ן)
- Maps between Hebrew and English filenames (e.g., '1samuel' → '1_samuel')
- Processes all books in texts/tanakh/ and texts/nasb/books/ directories
- Filename mapping handles differences:
  - Numbered books: 1samuel → 1_samuel (underscore added)
  - Song of Songs: songofsongs → song_of_solomon (name variation)

OUTPUT:
Generates results/ot_books_word_count_comparison_results.txt with:
- Side-by-side comparison of Hebrew vs English word counts for all OT books
- Books sorted by Hebrew/English ratio (lowest to highest)
- Statistical summary including total word counts across entire OT
- All 39 OT books included
"""

import re
import os
from pathlib import Path

def count_hebrew_words(file_path):
    """Count total words in a Hebrew text file."""
    total_words = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    for line in content.split('\n'):
        # Remove Unicode directional marks
        clean_line = re.sub(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', line).strip()

        if not clean_line or 'xxxx' in clean_line:
            continue

        # Look for pattern: number ׃number hebrew_text
        match = re.search(r'(\d+)\s+׃(\d+)\s+(.+)', clean_line)
        if match:
            hebrew_text = match.group(3).strip()

            # Remove final punctuation
            hebrew_text = re.sub(r'[׃פס]\s*$', '', hebrew_text).strip()

            # Deduplicate ketiv/qere: remove ketiv (marked with *word), keep qere (marked with **word)
            # Pattern: *ketiv **qere - we want to remove both markers and keep only qere
            hebrew_text = re.sub(r'\*\S+\s+\*\*', '**', hebrew_text)  # Remove ketiv, leave qere marker
            hebrew_text = re.sub(r'\*\*', '', hebrew_text)  # Remove qere marker

            # Split into words and handle maqqeph-separated words
            for word_group in hebrew_text.split():
                # Split by maqqeph and filter for Hebrew text
                maqqeph_parts = word_group.split('־')
                for part in maqqeph_parts:
                    # Keep parts that contain Hebrew characters
                    if part.strip() and any('\u0590' <= c <= '\u05FF' for c in part):
                        total_words += 1

    return total_words

def count_english_words(file_path):
    """Count total words in an English NASB text file."""
    total_words = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Skip chapter headers (e.g., "Genesis 1 New American Standard Bible")
        if re.match(r'^\w+\s+\d+\s+New American Standard Bible', line):
            continue

        # Check if line starts with a number (verse number)
        verse_match = re.match(r'^\d+\s+(.+)$', line)
        if verse_match:
            verse_text = verse_match.group(1).strip()
            # Count English words
            english_words = re.findall(r'\b\w+\b', verse_text)
            total_words += len(english_words)

    return total_words

def analyze_ot_books():
    """Analyze word counts for all Old Testament books."""

    hebrew_dir = Path("texts/tanakh")
    english_dir = Path("texts/nasb/books")

    # List of OT book names (Hebrew filename, English filename)
    # Most books use the same name, but some differ
    ot_books = [
        ('genesis', 'genesis'),
        ('exodus', 'exodus'),
        ('leviticus', 'leviticus'),
        ('numbers', 'numbers'),
        ('deuteronomy', 'deuteronomy'),
        ('joshua', 'joshua'),
        ('judges', 'judges'),
        ('ruth', 'ruth'),
        ('1samuel', '1_samuel'),
        ('2samuel', '2_samuel'),
        ('1kings', '1_kings'),
        ('2kings', '2_kings'),
        ('1chronicles', '1_chronicles'),
        ('2chronicles', '2_chronicles'),
        ('ezra', 'ezra'),
        ('nehemiah', 'nehemiah'),
        ('esther', 'esther'),
        ('job', 'job'),
        ('psalms', 'psalms'),
        ('proverbs', 'proverbs'),
        ('ecclesiastes', 'ecclesiastes'),
        ('songofsongs', 'song_of_solomon'),
        ('isaiah', 'isaiah'),
        ('jeremiah', 'jeremiah'),
        ('lamentations', 'lamentations'),
        ('ezekiel', 'ezekiel'),
        ('daniel', 'daniel'),
        ('hosea', 'hosea'),
        ('joel', 'joel'),
        ('amos', 'amos'),
        ('obadiah', 'obadiah'),
        ('jonah', 'jonah'),
        ('micah', 'micah'),
        ('nahum', 'nahum'),
        ('habakkuk', 'habakkuk'),
        ('zephaniah', 'zephaniah'),
        ('haggai', 'haggai'),
        ('zechariah', 'zechariah'),
        ('malachi', 'malachi'),
    ]

    book_data = []

    print("Analyzing Old Testament books...")

    for hebrew_name, english_name in ot_books:
        hebrew_file = hebrew_dir / f"{hebrew_name}.txt"
        english_file = english_dir / f"{english_name}.txt"

        if not hebrew_file.exists():
            print(f"  Warning: Hebrew file not found for {hebrew_name}")
            continue

        if not english_file.exists():
            print(f"  Warning: English file not found for {english_name}")
            continue

        # Use English name for display (more familiar)
        display_name = english_name.replace('_', ' ').title()
        print(f"  Processing {display_name}...")

        hebrew_count = count_hebrew_words(hebrew_file)
        english_count = count_english_words(english_file)

        if english_count > 0:
            ratio = hebrew_count / english_count
            book_data.append({
                'name': display_name,
                'hebrew_count': hebrew_count,
                'english_count': english_count,
                'ratio': ratio
            })

    # Sort by ratio (ascending - lowest ratios first)
    book_data.sort(key=lambda x: x['ratio'])

    # Display results
    print("\n" + "="*90)
    print("OLD TESTAMENT BOOKS: Hebrew vs English Word Counts")
    print("Sorted by Hebrew/English ratio (lowest = most concise Hebrew)")
    print("="*90)
    print(f"{'Book':<20} {'Hebrew Words':>15} {'English Words':>15} {'Ratio':>10}")
    print("-"*90)

    for book in book_data:
        print(f"{book['name']:<20} {book['hebrew_count']:>15,} {book['english_count']:>15,} {book['ratio']:>10.3f}")

    # Statistics
    print("\n" + "="*90)
    print("STATISTICS")
    print("="*90)

    total_hebrew = sum(b['hebrew_count'] for b in book_data)
    total_english = sum(b['english_count'] for b in book_data)
    avg_ratio = sum(b['ratio'] for b in book_data) / len(book_data)

    print(f"Total books analyzed: {len(book_data)}")
    print(f"Total Hebrew words (all OT): {total_hebrew:,}")
    print(f"Total English words (all OT): {total_english:,}")
    print(f"Overall Hebrew/English ratio: {total_hebrew/total_english:.3f}")
    print(f"Average book ratio: {avg_ratio:.3f}")
    print(f"Lowest ratio: {book_data[0]['ratio']:.3f} ({book_data[0]['name']})")
    print(f"Highest ratio: {book_data[-1]['ratio']:.3f} ({book_data[-1]['name']})")

    # Save to file
    output_file = "results/ot_books_word_count_comparison_results.txt"
    print(f"\nSaving results to '{output_file}'...")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("OLD TESTAMENT BOOKS: Hebrew vs English Word Counts\n")
        f.write("Sorted by Hebrew/English ratio (lowest = most concise Hebrew)\n")
        f.write("="*90 + "\n\n")
        f.write(f"{'Book':<20} {'Hebrew Words':>15} {'English Words':>15} {'Ratio':>10}\n")
        f.write("-"*90 + "\n")

        for book in book_data:
            f.write(f"{book['name']:<20} {book['hebrew_count']:>15,} {book['english_count']:>15,} {book['ratio']:>10.3f}\n")

        f.write("\n" + "="*90 + "\n")
        f.write("STATISTICS\n")
        f.write("="*90 + "\n")
        f.write(f"Total books analyzed: {len(book_data)}\n")
        f.write(f"Total Hebrew words (all OT): {total_hebrew:,}\n")
        f.write(f"Total English words (all OT): {total_english:,}\n")
        f.write(f"Overall Hebrew/English ratio: {total_hebrew/total_english:.3f}\n")
        f.write(f"Average book ratio: {avg_ratio:.3f}\n")
        f.write(f"Lowest ratio: {book_data[0]['ratio']:.3f} ({book_data[0]['name']})\n")
        f.write(f"Highest ratio: {book_data[-1]['ratio']:.3f} ({book_data[-1]['name']})\n")

    print("Analysis complete!")

if __name__ == "__main__":
    analyze_ot_books()
