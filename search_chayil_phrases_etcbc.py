"""
Search for occurrences of חיל (chayil) phrases in the Hebrew Bible using ETCBC dataset.

This script uses the ETCBC BHSA (Biblia Hebraica Stuttgartensia Amstelodamensis) dataset
via Text-Fabric to find all variants of three phrase patterns:
1. אֵשֶׁת חַיִל (eshet chayil) - "woman of valor/worth" and variants
2. גִּבּוֹר חַיִל (gibbor chayil) - "mighty man of valor" and variants
3. אִישׁ חָיִל (ish chayil) - "man of valor/worth" and variants

Using ETCBC allows us to search by lemma (base form), which catches:
- Singular and plural forms
- Construct states (e.g., אַנְשֵׁי = "men of")
- Different vowel pointings and cantillation

The script:
- Loads ETCBC BHSA dataset via Text-Fabric
- Searches for consecutive word pairs where first word's lemma matches one of the target
  words (woman/man/mighty) and second word's lemma is חיל
- Extracts complete verses with book, chapter, verse references
- Groups results by phrase pattern

Output: results/search_chayil_phrases_etcbc_results.txt
"""

import os
import sys
from collections import defaultdict

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Safe print handler for Hebrew text
class SafeUnicodeHandler:
    def safe_print(self, text):
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = str(text).encode('ascii', errors='replace').decode('ascii')
            print(safe_text)

safe_handler = SafeUnicodeHandler()

def load_etcbc():
    """Load the ETCBC BHSA dataset."""
    print("Loading ETCBC BHSA dataset...")
    try:
        from tf.app import use
        A = use('etcbc/bhsa', silent=True)
        print("✓ Dataset loaded successfully\n")
        return A
    except Exception as e:
        print(f"Error loading ETCBC dataset: {e}")
        return None

def get_verse_text(A, verse_node):
    """Get the full text of a verse."""
    try:
        # Get all words in the verse using downward edges
        word_nodes = A.api.L.d(verse_node, otype='word')

        # Get the vocalized text of each word
        words = []
        for word in word_nodes:
            try:
                # Use g_word_utf8 for full word form with vocalization
                word_text = A.api.F.g_word_utf8.v(word)
                if word_text:
                    words.append(word_text)
            except:
                pass

        return ' '.join(words)
    except:
        return ""

def get_verse_reference(A, word_node):
    """Get book, chapter, verse reference for a word."""
    try:
        # Navigate up to verse node
        verse_node = A.api.L.u(word_node, otype='verse')[0]

        # Get book, chapter, verse numbers
        book = A.api.F.book.v(verse_node)
        chapter = A.api.F.chapter.v(verse_node)
        verse = A.api.F.verse.v(verse_node)

        return book, chapter, verse, verse_node
    except:
        return None, None, None, None

def search_chayil_phrases(A):
    """
    Search for all חיל phrase variants.

    Target lemmas (transliterated in ETCBC):
    - >JC/ (אִישׁ) = man
    - >C$H (אִשָּׁה) = woman
    - GBWR (גִּבּוֹר) = mighty man
    - XJL (חַיִל) = valor, strength, army

    Note: ETCBC uses specific transliteration conventions.
    """
    print("Searching for חיל phrases...")

    # Dictionary to store results: phrase_type -> list of (book, ch, v, word1, word2, verse_text)
    results = defaultdict(list)

    # Get all word nodes
    print("  Getting all words from Hebrew Bible...")
    all_words = A.search('word')
    print(f"  Found {len(all_words)} words total")

    # Process each word and check if next word forms a target phrase
    print("  Analyzing word pairs...")
    checked_count = 0

    for word_result in all_words:
        # Extract word node from result tuple
        word1_node = word_result[0] if isinstance(word_result, tuple) else word_result

        checked_count += 1
        if checked_count % 100000 == 0:
            print(f"    Checked {checked_count:,} words...")

        try:
            # Get lemma of first word
            lemma1 = A.api.F.lex.v(word1_node)
            if not lemma1:
                continue

            # Check if this is one of our target first words
            # Note: ETCBC lemmas have trailing slash
            phrase_type = None
            if lemma1 == '>JC/':  # אִישׁ (man)
                phrase_type = 'ish_chayil'
            elif lemma1 == '>CH/':  # אִשָּׁה (woman) - Note: >CH/ not >C$H/
                phrase_type = 'eshet_chayil'
            elif lemma1 == 'GBWR/':  # גִּבּוֹר (mighty)
                phrase_type = 'gibbor_chayil'

            if not phrase_type:
                continue

            # Get the next word in sequence
            verse_node = A.api.L.u(word1_node, otype='verse')
            if not verse_node:
                continue
            verse_node = verse_node[0]

            verse_words = A.api.L.d(verse_node, otype='word')

            # Find position of current word in verse
            word1_pos = None
            for i, w in enumerate(verse_words):
                if w == word1_node:
                    word1_pos = i
                    break

            if word1_pos is None or word1_pos >= len(verse_words) - 1:
                continue

            # Get next word - but check if there's a definite article (H) in between
            # Pattern 1: word1 word2 (adjacent)
            # Pattern 2: word1 H word2 (with definite article)
            word2_node = None
            word2_pos = None

            # Check immediately following word
            next_word = verse_words[word1_pos + 1]
            next_lemma = A.api.F.lex.v(next_word)

            if next_lemma == 'XJL/':
                # Direct adjacency: word1 word2
                word2_node = next_word
                word2_pos = word1_pos + 1
            elif next_lemma == 'H' and word1_pos + 2 < len(verse_words):
                # Check if pattern is: word1 H word2
                word_after_article = verse_words[word1_pos + 2]
                lemma_after_article = A.api.F.lex.v(word_after_article)
                if lemma_after_article == 'XJL/':
                    word2_node = word_after_article
                    word2_pos = word1_pos + 2

            if not word2_node:
                continue

            # Found a match! (we already verified lemma2 == 'XJL/' above)
            book, chapter, verse, verse_node = get_verse_reference(A, word1_node)

            if book:
                # Get vocalized forms
                word1_text = A.api.F.g_word_utf8.v(word1_node) or ""
                word2_text = A.api.F.g_word_utf8.v(word2_node) or ""

                # Get full verse text
                verse_text = get_verse_text(A, verse_node)

                # Store result
                results[phrase_type].append({
                    'book': book,
                    'chapter': chapter,
                    'verse': verse,
                    'word1': word1_text,
                    'word2': word2_text,
                    'phrase': f"{word1_text} {word2_text}",
                    'verse_text': verse_text,
                    'lemma1': lemma1,
                    'lemma2': 'XJL/'
                })

        except Exception as e:
            # Skip errors in individual word processing
            continue

    print(f"  ✓ Finished checking {checked_count:,} words\n")
    return results

def format_phrase_name(phrase_type):
    """Format phrase type for display."""
    names = {
        'eshet_chayil': 'אֵשֶׁת חַיִל (eshet chayil) - woman of valor',
        'gibbor_chayil': 'גִּבּוֹר חַיִל (gibbor chayil) - mighty man of valor',
        'ish_chayil': 'אִישׁ חָיִל (ish chayil) - man of valor'
    }
    return names.get(phrase_type, phrase_type)

def write_results(results):
    """Write results to output file."""
    # Create results directory if needed
    os.makedirs('results', exist_ok=True)

    output_file = os.path.join('results', 'search_chayil_phrases_etcbc_results.txt')

    # Calculate totals
    total_count = sum(len(matches) for matches in results.values())

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Search Results: חיל (chayil) Phrases in the Hebrew Bible\n")
        f.write("Using ETCBC BHSA Dataset (includes all grammatical variants)\n")
        f.write("=" * 80 + "\n\n")
        f.write("Phrases searched (by lemma, includes plurals and construct forms):\n")
        f.write("  1. אֵשֶׁת חַיִל (eshet chayil) - woman of valor/worth\n")
        f.write("  2. גִּבּוֹר חַיִל (gibbor chayil) - mighty man of valor\n")
        f.write("  3. אִישׁ חָיִל (ish chayil) - man of valor/worth\n\n")
        f.write(f"Total occurrences found: {total_count}\n")
        f.write("=" * 80 + "\n\n")

        # Write results grouped by phrase type
        for phrase_type in ['eshet_chayil', 'gibbor_chayil', 'ish_chayil']:
            if phrase_type in results:
                matches = results[phrase_type]
                f.write(f"\n{format_phrase_name(phrase_type)}\n")
                f.write("-" * 80 + "\n")
                f.write(f"Found {len(matches)} occurrence(s)\n\n")

                for match in matches:
                    f.write(f"{match['book']} {match['chapter']}:{match['verse']}\n")
                    f.write(f"  Matched: {match['phrase']}\n")
                    f.write(f"  Lemmas: {match['lemma1']} + {match['lemma2']}\n")
                    f.write(f"  {match['verse_text']}\n\n")

    return output_file, total_count

def main():
    # Load ETCBC dataset
    A = load_etcbc()
    if not A:
        print("Failed to load ETCBC dataset. Please ensure text-fabric is installed:")
        print("  pip install text-fabric")
        return

    # Search for phrases
    results = search_chayil_phrases(A)

    # Write results
    output_file, total_count = write_results(results)

    # Print summary
    print("=" * 80)
    print(f"✓ Search complete!")
    print(f"  Total occurrences: {total_count}")
    print(f"  Results saved to: {output_file}")
    print("\nSummary by phrase type:")

    for phrase_type in ['eshet_chayil', 'gibbor_chayil', 'ish_chayil']:
        if phrase_type in results:
            count = len(results[phrase_type])
            safe_handler.safe_print(f"  {format_phrase_name(phrase_type)}: {count}")

    print("=" * 80)

if __name__ == '__main__':
    main()
