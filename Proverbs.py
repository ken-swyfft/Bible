import re
from collections import Counter

# Unicode code points to manage
ETNACHTA = '\u0591'   # ֑
SOF_PASUQ = '\u05C3'  # ׃
MAQAF     = '\u05BE'  # ־

# Regex of Hebrew niqqud + most cantillation (KEEP etnachta)
# Hebrew combining marks: \u0591-\u05BD, \u05BF-\u05C7
# We remove all except \u0591 (etnachta). Also keep SOF_PASUQ and MAQAF.
REMOVE = ''.join(chr(c) for c in list(range(0x0591,0x05BE)) + list(range(0x05BF,0x05C8)))
# Put etnachta back (don’t remove it)
REMOVE = REMOVE.replace(ETNACHTA, '')
DIACRITICS_RE = re.compile(f"[{re.escape(REMOVE)}]")

def normalize(line: str, keep_maqaf=True) -> str:
    # Remove diacritics except etnachta; keep sof pasuq and (optionally) maqaf
    s = DIACRITICS_RE.sub('', line)
    if not keep_maqaf:
        s = s.replace(MAQAF, ' ')
    return s

def tokenize(colon: str, split_maqaf=True):
    if split_maqaf:
        colon = colon.replace(MAQAF, ' ')  # split words bound by maqaf
    # collapse punctuation except Hebrew letters, sof pasuq, etnachta already stripped/kept
    # remove sof pasuq if present inside the colon
    colon = colon.replace(SOF_PASUQ, ' ')
    # normalize spaces
    colon = re.sub(r'\s+', ' ', colon).strip()
    return [w for w in colon.split(' ') if w]

def count_4_3(proverbs_lines):
    """
    proverbs_lines: iterable of raw Hebrew verse lines for Proverbs,
    each containing exactly one verse (ending with sof pasuq ׃).
    """
    totals = Counter()
    examples = {'4+3': [], '3+4': []}
    for line in proverbs_lines:
        s = normalize(line, keep_maqaf=True)

        # Find the position of etnachta
        if ETNACHTA not in s:
            continue  # skip verses without etnachta

        # Split the text into words using spaces, preserving the etnachta position
        # First replace punctuation and collapse spaces, but keep etnachta
        working_text = s.replace(SOF_PASUQ, ' ')
        working_text = re.sub(r'\s+', ' ', working_text).strip()

        # Split on spaces to get words (some will contain etnachta)
        words = working_text.split(' ')
        words = [w for w in words if w]  # Remove empty strings

        # Find which word contains the etnachta
        word_with_etnachta = -1
        for i, word in enumerate(words):
            if ETNACHTA in word:
                word_with_etnachta = i
                break

        # Split after the word that contains etnachta
        if word_with_etnachta >= 0:
            left_words = words[:word_with_etnachta + 1]  # Include the word with etnachta
            right_words = words[word_with_etnachta + 1:]  # Everything after

            # Clean up the words by removing etnachta for counting
            left_clean = [w.replace(ETNACHTA, '') for w in left_words if w.replace(ETNACHTA, '')]
            right_clean = [w.replace(ETNACHTA, '') for w in right_words if w.replace(ETNACHTA, '')]

            # Further tokenize if needed (split on maqaf)
            left_tokens = []
            for word in left_clean:
                left_tokens.extend(tokenize(word, split_maqaf=True))

            right_tokens = []
            for word in right_clean:
                right_tokens.extend(tokenize(word, split_maqaf=True))

            L = len(left_tokens)
            R = len(right_tokens)

            if L > 0 and R > 0:  # Only count if we have words on both sides
                totals['bicola'] += 1
                if (L, R) == (4, 3):
                    totals['4+3'] += 1
                    if len(examples['4+3']) < 10:
                        examples['4+3'].append(line.strip())
                elif (L, R) == (3, 4):
                    totals['3+4'] += 1
                    if len(examples['3+4']) < 10:
                        examples['3+4'].append(line.strip())

    return totals, examples

def load_proverbs_text(filename='Proverbs.txt'):
    """Load Proverbs text file and extract verse lines from chapter 10 onwards."""
    lines = []
    in_chapter_10_or_later = False

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue

            # Check for chapter markers first (before filtering xxxx)
            if 'Chapter' in line:
                if 'Chapter 10' in line:
                    in_chapter_10_or_later = True
                continue

            # Skip header lines that contain xxxx (but not chapter lines)
            if 'xxxx' in line and 'Chapter' not in line:
                continue

            # Only process verses if we're in chapter 10 or later
            if not in_chapter_10_or_later:
                continue

            # Look for verse lines that contain Hebrew text
            if '׃' in line and any(c for c in line if '\u0590' <= c <= '\u05FF'):
                # Remove directional marks
                clean_line = ''.join(c for c in line if c not in '\u202A\u202B\u202C\u202D\u202E\u2066\u2067\u2068\u2069')

                # Pattern: " 1  ׃10   [Hebrew text]׃"
                # Find the last occurrence of numbers followed by ׃, then extract Hebrew text after that
                import re
                # Look for the pattern: digits/spaces + ׃ + digits/spaces + Hebrew text + ׃
                match = re.search(r'\d+\s*׃\d*\s+([^׃]*׃)', clean_line)
                if match:
                    hebrew_text = match.group(1).strip()
                    if hebrew_text and any('\u0590' <= c <= '\u05FF' for c in hebrew_text):
                        lines.append(hebrew_text)
    return lines

# --- Main execution ---
if __name__ == "__main__":
    # Load Proverbs text
    lines = load_proverbs_text()

    # Analyze the text
    totals, examples = count_4_3(lines)
    bicola = totals['bicola']
    pct_43 = 100 * totals['4+3'] / bicola if bicola else 0.0
    pct_34 = 100 * totals['3+4'] / bicola if bicola else 0.0

    print(f"Total verses loaded: {len(lines)}")
    print(f"Bicola counted: {bicola}")
    print(f"4+3: {totals['4+3']} ({pct_43:.1f}%)")
    print(f"3+4: {totals['3+4']} ({pct_34:.1f}%)")
    print("\nExamples 4+3:")
    for example in examples['4+3']:
        try:
            print(f"- {example}")
        except UnicodeEncodeError:
            print(f"- [Hebrew text - encoding issue]")
    print("\nExamples 3+4:")
    for example in examples['3+4']:
        try:
            print(f"- {example}")
        except UnicodeEncodeError:
            print(f"- [Hebrew text - encoding issue]")
