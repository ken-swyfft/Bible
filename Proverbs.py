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
        # Split on etnachta; some texts may have multiple occurrences—expect 1 in bicola
        parts = s.split(ETNACHTA)
        if len(parts) != 2:
            continue  # skip non-bicola
        left, right = parts[0], parts[1]
        L = len(tokenize(left, split_maqaf=True))
        R = len(tokenize(right, split_maqaf=True))
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
    """Load Proverbs text file and extract verse lines."""
    lines = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip header lines and empty lines
            if not line or 'xxxx' in line:
                continue
            # Look for verse lines that contain Hebrew text
            if '׃' in line and any(c for c in line if '\u0590' <= c <= '\u05FF'):
                # Remove directional marks and extract Hebrew text
                clean_line = ''.join(c for c in line if c not in '\u202A\u202B\u202C\u202D\u202E\u2066\u2067\u2068\u2069')

                # Find the Hebrew text part (after verse number, before final ׃)
                # Look for pattern like "1  ׃1   [Hebrew text]׃"
                parts = clean_line.split('׃')
                if len(parts) >= 3:
                    # The Hebrew text is typically the last part before the final ׃
                    hebrew_text = parts[-2].strip()
                    if hebrew_text and any('\u0590' <= c <= '\u05FF' for c in hebrew_text):
                        lines.append(hebrew_text + '׃')
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
