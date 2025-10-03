#!/usr/bin/env python3
"""
PROVERBS HEBREW VS ENGLISH WORD COUNT ANALYSIS

PURPOSE:
This script compares word counts between the original Hebrew text of Proverbs and its English
translation (NASB) to identify verses where Hebrew is most concise relative to English,
as well as verses where Hebrew uses more words. Demonstrates the variation in Hebrew
grammatical structures and translation patterns.

METHODOLOGY:
1. Parses Hebrew Proverbs from Westminster Leningrad Codex (UXLC format)
2. Parses English Proverbs from New American Standard Bible (NASB)
3. Counts words in both languages using linguistically appropriate methods:
   - Hebrew: Treats maqqeph (־) separated words as individual words
   - English: Uses word boundary regex to handle punctuation properly
4. Calculates Hebrew/English ratios for each verse
5. Identifies verses with both the lowest and highest ratios

TECHNICAL APPROACH:
- Hebrew parsing: Handles Unicode directional marks, verse patterns (num ׃num text)
- Maqqeph handling: Splits words connected by ־ for accurate Hebrew word counts
- English parsing: Detects chapter headers, processes verse-by-verse
- Unicode safety: Handles Hebrew text encoding issues in Windows console
- Bilingual alignment: Matches verses by chapter:verse references

LINGUISTIC SIGNIFICANCE:
Hebrew's grammatical features (verbal conjugations, construct chains, compressed syntax)
often express ideas that require multiple words in English. This analysis quantifies
that efficiency and identifies the most striking examples.

OUTPUT:
Generates results/proverbs_analyze_word_ratios_results.txt with:
- Top 20 verses with lowest Hebrew/English word ratios (most Hebrew efficiency)
- Top 20 verses with highest Hebrew/English word ratios (Hebrew more verbose)
- Statistical summary of translation expansion patterns
- Full Hebrew text with accurate word counts
"""

import re
import os

def parse_hebrew_proverbs(file_path):
    """Parse Hebrew Proverbs file and extract verses with word counts."""
    verses = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Look for verse patterns - the format includes Unicode directional marks
    # Pattern: verse_num ׃chapter_num hebrew_text
    # Note: lines may start with Unicode directional marks

    for line in content.split('\n'):
        # Remove Unicode directional marks and other control characters
        clean_line = re.sub(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', line).strip()

        if not clean_line or 'xxxx' in clean_line:
            continue

        # Look for pattern: number ׃number hebrew_text
        match = re.search(r'(\d+)\s+׃(\d+)\s+(.+)', clean_line)
        if match:
            verse_num = int(match.group(1))
            chapter_num = int(match.group(2))
            hebrew_text = match.group(3).strip()

            # Remove final punctuation and split into words
            # Remove common Hebrew punctuation like ׃ פ ס at the end
            hebrew_text = re.sub(r'[׃פס]\s*$', '', hebrew_text).strip()

            # Deduplicate ketiv/qere: remove ketiv (marked with *word), keep qere (marked with **word)
            # Pattern: *ketiv **qere - we want to remove both markers and keep only qere
            hebrew_text = re.sub(r'\*\S+\s+\*\*', '**', hebrew_text)  # Remove ketiv, leave qere marker
            hebrew_text = re.sub(r'\*\*', '', hebrew_text)  # Remove qere marker

            # Split into words and handle maqqeph-separated words
            # First split by spaces, then split by maqqeph (־) to count each part as a separate word
            hebrew_words = []
            for word_group in hebrew_text.split():
                # Split by maqqeph and filter for Hebrew text
                maqqeph_parts = word_group.split('־')
                for part in maqqeph_parts:
                    # Keep parts that contain Hebrew characters (including vowel points and cantillation)
                    if part.strip() and any('\u0590' <= c <= '\u05FF' for c in part):
                        hebrew_words.append(part.strip())

            verse_ref = f"{chapter_num}:{verse_num}"
            verses[verse_ref] = {
                'hebrew_text': hebrew_text,
                'hebrew_word_count': len(hebrew_words),
                'hebrew_words': hebrew_words
            }

    return verses

def parse_english_proverbs(file_path):
    """Parse English NASB Proverbs file and extract verses with word counts."""
    verses = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    current_chapter = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for chapter headers like "Proverbs 1 New American Standard Bible"
        chapter_match = re.match(r'^Proverbs (\d+)', line)
        if chapter_match:
            current_chapter = int(chapter_match.group(1))
            continue

        # Check if line starts with a number (verse number)
        verse_match = re.match(r'^(\d+)\s+(.+)$', line)
        if verse_match and current_chapter > 0:
            verse_num = int(verse_match.group(1))
            verse_text = verse_match.group(2).strip()

            # Count English words (split by whitespace, remove punctuation for counting)
            english_words = re.findall(r'\b\w+\b', verse_text)

            verse_ref = f"{current_chapter}:{verse_num}"
            verses[verse_ref] = {
                'english_text': verse_text,
                'english_word_count': len(english_words),
                'english_words': english_words
            }

    return verses

def analyze_word_ratios():
    """Analyze Hebrew to English word count ratios in Proverbs."""

    # File paths
    hebrew_file = "texts/tanakh/proverbs.txt"
    english_file = "texts/nasb/books/proverbs.txt"

    # Check if files exist
    if not os.path.exists(hebrew_file):
        print(f"Hebrew file not found: {hebrew_file}")
        return
    if not os.path.exists(english_file):
        print(f"English file not found: {english_file}")
        return

    print("Parsing Hebrew Proverbs...")
    hebrew_verses = parse_hebrew_proverbs(hebrew_file)
    print(f"Found {len(hebrew_verses)} Hebrew verses")

    print("Parsing English Proverbs...")
    english_verses = parse_english_proverbs(english_file)
    print(f"Found {len(english_verses)} English verses")

    # Match verses and calculate ratios
    ratios = []

    for verse_ref in hebrew_verses:
        if verse_ref in english_verses:
            hebrew_count = hebrew_verses[verse_ref]['hebrew_word_count']
            english_count = english_verses[verse_ref]['english_word_count']

            if english_count > 0:  # Avoid division by zero
                ratio = hebrew_count / english_count
                ratios.append({
                    'verse': verse_ref,
                    'hebrew_count': hebrew_count,
                    'english_count': english_count,
                    'ratio': ratio,
                    'hebrew_text': hebrew_verses[verse_ref]['hebrew_text'],
                    'english_text': english_verses[verse_ref]['english_text']
                })

    # Sort by ratio (ascending - lowest ratios first)
    ratios.sort(key=lambda x: x['ratio'])

    print(f"\nAnalyzed {len(ratios)} matching verses")
    print("\n" + "="*80)
    print("TOP 20 VERSES: Fewest Hebrew words relative to English words")
    print("="*80)

    for i, verse_data in enumerate(ratios[:20], 1):
        print(f"\n{i}. Proverbs {verse_data['verse']}")
        print(f"   Ratio: {verse_data['ratio']:.3f} ({verse_data['hebrew_count']} Hebrew / {verse_data['english_count']} English)")
        try:
            print(f"   Hebrew: {verse_data['hebrew_text']}")
        except UnicodeEncodeError:
            print(f"   Hebrew: [Hebrew text - {verse_data['hebrew_count']} words]")
        print(f"   English: {verse_data['english_text']}")

    print("\n" + "="*80)
    print("TOP 20 VERSES: Most Hebrew words relative to English words")
    print("="*80)

    for i, verse_data in enumerate(ratios[-20:], 1):
        print(f"\n{i}. Proverbs {verse_data['verse']}")
        print(f"   Ratio: {verse_data['ratio']:.3f} ({verse_data['hebrew_count']} Hebrew / {verse_data['english_count']} English)")
        try:
            print(f"   Hebrew: {verse_data['hebrew_text']}")
        except UnicodeEncodeError:
            print(f"   Hebrew: [Hebrew text - {verse_data['hebrew_count']} words]")
        print(f"   English: {verse_data['english_text']}")

    # Also show some statistics
    print(f"\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    if ratios:
        # Calculate total word counts
        total_hebrew_words = sum(r['hebrew_count'] for r in ratios)
        total_english_words = sum(r['english_count'] for r in ratios)

        avg_ratio = sum(r['ratio'] for r in ratios) / len(ratios)
        print(f"Total Hebrew words in Proverbs: {total_hebrew_words:,}")
        print(f"Total English words in Proverbs: {total_english_words:,}")
        print(f"Overall Hebrew/English ratio: {total_hebrew_words/total_english_words:.3f}")
        print(f"Average Hebrew/English ratio: {avg_ratio:.3f}")
        print(f"Lowest ratio: {ratios[0]['ratio']:.3f} (Proverbs {ratios[0]['verse']})")
        print(f"Highest ratio: {ratios[-1]['ratio']:.3f} (Proverbs {ratios[-1]['verse']})")

if __name__ == "__main__":
    analyze_word_ratios()

    # Save results to file
    print(f"\nSaving detailed results to 'results/proverbs_analyze_word_ratios_results.txt'...")

    with open("results/proverbs_analyze_word_ratios_results.txt", "w", encoding="utf-8") as f:
        # Re-run analysis but write to file (reuse the already parsed data)
        hebrew_file = "texts/tanakh/proverbs.txt"
        english_file = "texts/nasb/books/proverbs.txt"

        hebrew_verses = parse_hebrew_proverbs(hebrew_file)
        english_verses = parse_english_proverbs(english_file)

        ratios = []
        for verse_ref in hebrew_verses:
            if verse_ref in english_verses:
                hebrew_count = hebrew_verses[verse_ref]['hebrew_word_count']
                english_count = english_verses[verse_ref]['english_word_count']
                if english_count > 0:
                    ratio = hebrew_count / english_count
                    ratios.append({
                        'verse': verse_ref,
                        'hebrew_count': hebrew_count,
                        'english_count': english_count,
                        'ratio': ratio,
                        'hebrew_text': hebrew_verses[verse_ref]['hebrew_text'],
                        'english_text': english_verses[verse_ref]['english_text']
                    })

        ratios.sort(key=lambda x: x['ratio'])

        f.write("PROVERBS WORD RATIO ANALYSIS\n")
        f.write("Hebrew vs English Word Count Ratios\n")
        f.write("="*80 + "\n\n")
        f.write("TOP 20 VERSES: Fewest Hebrew words relative to English words\n")
        f.write("="*80 + "\n")

        for i, verse_data in enumerate(ratios[:20], 1):
            f.write(f"\n{i}. Proverbs {verse_data['verse']}\n")
            f.write(f"   Ratio: {verse_data['ratio']:.3f} ({verse_data['hebrew_count']} Hebrew / {verse_data['english_count']} English)\n")
            f.write(f"   Hebrew: {verse_data['hebrew_text']}\n")
            f.write(f"   English: {verse_data['english_text']}\n")

        f.write("\n" + "="*80 + "\n")
        f.write("TOP 20 VERSES: Most Hebrew words relative to English words\n")
        f.write("="*80 + "\n")

        for i, verse_data in enumerate(ratios[-20:], 1):
            f.write(f"\n{i}. Proverbs {verse_data['verse']}\n")
            f.write(f"   Ratio: {verse_data['ratio']:.3f} ({verse_data['hebrew_count']} Hebrew / {verse_data['english_count']} English)\n")
            f.write(f"   Hebrew: {verse_data['hebrew_text']}\n")
            f.write(f"   English: {verse_data['english_text']}\n")

        f.write(f"\n" + "="*80 + "\n")
        f.write("STATISTICS\n")
        f.write("="*80 + "\n")
        if ratios:
            # Calculate total word counts
            total_hebrew_words = sum(r['hebrew_count'] for r in ratios)
            total_english_words = sum(r['english_count'] for r in ratios)

            avg_ratio = sum(r['ratio'] for r in ratios) / len(ratios)
            f.write(f"Total Hebrew words in Proverbs: {total_hebrew_words:,}\n")
            f.write(f"Total English words in Proverbs: {total_english_words:,}\n")
            f.write(f"Overall Hebrew/English ratio: {total_hebrew_words/total_english_words:.3f}\n")
            f.write(f"Average Hebrew/English ratio: {avg_ratio:.3f}\n")
            f.write(f"Lowest ratio: {ratios[0]['ratio']:.3f} (Proverbs {ratios[0]['verse']})\n")
            f.write(f"Highest ratio: {ratios[-1]['ratio']:.3f} (Proverbs {ratios[-1]['verse']})\n")
            f.write(f"Total verses analyzed: {len(ratios)}\n")

    print("Analysis complete!")