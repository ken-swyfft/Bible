"""
Search for occurrences of חיל (chayil) phrases in the Hebrew Bible.

This script searches for three specific phrase patterns and their variants:
1. אֵשֶׁת חַיִל (eshet chayil) - "woman of valor/worth"
2. גִּבּוֹר חַיִל (gibbor chayil) - "mighty man of valor"
3. אִישׁ חָיִל (ish chayil) - "man of valor/worth"

The script:
- Reads all Hebrew Bible texts from ./texts/tanakh/
- Removes Unicode directional marks and verse markers
- Handles ketiv/qere variants (keeps qere)
- Searches for the root words regardless of vowel points and cantillation
- Extracts complete verses containing any of these phrases
- Outputs results with book, chapter, verse references and full verse text

Output: results/search_chayil_phrases_results.txt
"""

import os
import re
import glob
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def clean_hebrew_text(text):
    """Remove Unicode directional marks from Hebrew text."""
    return re.sub(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', text)

def deduplicate_ketiv_qere(text):
    """Remove ketiv, keep qere (read form)."""
    # Remove ketiv word (marked with *), keep qere marker
    text = re.sub(r'\*\S+\s+\*\*', '**', text)
    # Remove qere marker
    text = re.sub(r'\*\*', '', text)
    return text

def remove_vowels_cantillation(word):
    """
    Remove vowel points and cantillation marks from Hebrew word.
    Keeps only consonants for matching.
    Hebrew consonants: \u05d0-\u05ea
    Vowels and cantillation: \u0591-\u05c7
    """
    # Keep only Hebrew consonants
    return ''.join(c for c in word if '\u05d0' <= c <= '\u05ea')

def extract_verse_reference(line):
    """
    Extract verse number and chapter from line.
    Format: "verse_num ׃chapter_num text"
    Example: "1 ׃2 text..." means chapter 2, verse 1
    """
    match = re.match(r'\s*(\d+)\s*׃(\d+)\s+(.+)', line)
    if match:
        verse_num = match.group(1)
        chapter_num = match.group(2)
        text = match.group(3)
        return verse_num, chapter_num, text
    return None, None, None

def search_phrases_in_text(text):
    """
    Search for the three phrase patterns in Hebrew text.
    Returns list of tuples: (phrase_type, matched_text)

    The three patterns (consonants only):
    1. אשת חיל (eshet chayil) - consonants: אשת חיל
    2. גבור חיל (gibbor chayil) - consonants: גבור חיל
    3. איש חיל (ish chayil) - consonants: איש חיל
    """
    matches = []

    # Split text into words (split on whitespace and maqqeph)
    words = re.split(r'[\s־]+', text)

    # Remove vowels/cantillation from all words for comparison
    consonant_words = [remove_vowels_cantillation(w) for w in words]

    # Define the three phrase patterns (consonants only)
    patterns = {
        'eshet_chayil': ['אשת', 'חיל'],
        'gibbor_chayil': ['גבור', 'חיל'],
        'ish_chayil': ['איש', 'חיל']
    }

    # Look for consecutive word pairs matching our patterns
    for i in range(len(consonant_words) - 1):
        word1 = consonant_words[i]
        word2 = consonant_words[i + 1]

        # Check each pattern
        for phrase_name, (pattern1, pattern2) in patterns.items():
            if word1 == pattern1 and word2 == pattern2:
                # Get the original vocalized words
                matched_text = words[i] + ' ' + words[i + 1]
                matches.append((phrase_name, matched_text))

    return matches

def process_book(filepath):
    """
    Process a single book file and search for the phrases.
    Returns list of tuples: (book_name, chapter, verse, phrase_type, matched_text, full_verse)
    """
    results = []
    book_name = os.path.basename(filepath).replace('.txt', '').title()
    current_chapter = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = clean_hebrew_text(line)

            # Skip header lines
            if line.strip().startswith('xxxx') or not line.strip():
                continue

            # Extract verse reference and text
            verse_num, chapter_num, verse_text = extract_verse_reference(line)

            if verse_num is None:
                continue

            # Update current chapter
            if chapter_num:
                current_chapter = chapter_num

            # Clean up the verse text
            verse_text = deduplicate_ketiv_qere(verse_text)
            verse_text = re.sub(r'[׃פס]\s*$', '', verse_text)  # Remove end markers

            # Search for phrases
            matches = search_phrases_in_text(verse_text)

            if matches:
                for phrase_type, matched_text in matches:
                    results.append((
                        book_name,
                        current_chapter,
                        verse_num,
                        phrase_type,
                        matched_text,
                        verse_text.strip()
                    ))

    return results

def format_phrase_name(phrase_type):
    """Format phrase type for display."""
    names = {
        'eshet_chayil': 'אֵשֶׁת חַיִל (eshet chayil)',
        'gibbor_chayil': 'גִּבּוֹר חַיִל (gibbor chayil)',
        'ish_chayil': 'אִישׁ חָיִל (ish chayil)'
    }
    return names.get(phrase_type, phrase_type)

def main():
    # Find all Hebrew Bible books
    tanakh_path = os.path.join('texts', 'tanakh', '*.txt')
    book_files = glob.glob(tanakh_path)

    if not book_files:
        print("Error: No Hebrew text files found in texts/tanakh/")
        return

    print(f"Searching {len(book_files)} books for חיל phrases...")

    all_results = []

    # Process each book
    for filepath in sorted(book_files):
        book_results = process_book(filepath)
        all_results.extend(book_results)
        if book_results:
            print(f"  {os.path.basename(filepath)}: {len(book_results)} occurrence(s)")

    # Create results directory if it doesn't exist
    os.makedirs('results', exist_ok=True)

    # Write results to file
    output_file = os.path.join('results', 'search_chayil_phrases_results.txt')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Search Results: חיל (chayil) Phrases in the Hebrew Bible\n")
        f.write("=" * 80 + "\n\n")
        f.write("Phrases searched:\n")
        f.write("  1. אֵשֶׁת חַיִל (eshet chayil) - woman of valor/worth\n")
        f.write("  2. גִּבּוֹר חַיִל (gibbor chayil) - mighty man of valor\n")
        f.write("  3. אִישׁ חָיִל (ish chayil) - man of valor/worth\n\n")
        f.write(f"Total occurrences found: {len(all_results)}\n")
        f.write("=" * 80 + "\n\n")

        # Group results by phrase type
        by_phrase = {}
        for result in all_results:
            phrase_type = result[3]
            if phrase_type not in by_phrase:
                by_phrase[phrase_type] = []
            by_phrase[phrase_type].append(result)

        # Write results grouped by phrase type
        for phrase_type in ['eshet_chayil', 'gibbor_chayil', 'ish_chayil']:
            if phrase_type in by_phrase:
                results = by_phrase[phrase_type]
                f.write(f"\n{format_phrase_name(phrase_type)}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Found {len(results)} occurrence(s)\n\n")

                for book, chapter, verse, _, matched_text, full_verse in results:
                    f.write(f"{book} {chapter}:{verse}\n")
                    f.write(f"  Matched: {matched_text}\n")
                    f.write(f"  {full_verse}\n\n")

    print(f"\n✓ Search complete!")
    print(f"  Total occurrences: {len(all_results)}")
    print(f"  Results saved to: {output_file}")

    # Print summary by phrase type
    print("\nSummary by phrase type:")
    for phrase_type in ['eshet_chayil', 'gibbor_chayil', 'ish_chayil']:
        if phrase_type in by_phrase:
            count = len(by_phrase[phrase_type])
            print(f"  {format_phrase_name(phrase_type)}: {count}")

if __name__ == '__main__':
    main()
