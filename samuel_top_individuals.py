"""
Count the top individuals mentioned in 1 and 2 Samuel.

This script uses the ETCBC BHSA (Text-Fabric) database to:
1. Load all words from Samuel_I and Samuel_II
2. Filter for proper nouns (names of persons)
3. Count occurrences by lemma
4. Return the top 5 individuals with precise counts

ETCBC book names:
- 1 Samuel = 'Samuel_I'
- 2 Samuel = 'Samuel_II'
"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

from tf.app import use
from collections import Counter

# Load BHSA dataset
print("Loading ETCBC BHSA dataset...")
A = use('etcbc/bhsa', silent=True)
print("Dataset loaded.\n")

# Get word nodes from both Samuel books
def get_book_words(book_name):
    """Get all word nodes from a book."""
    book_results = A.search(f'book book={book_name}')
    if not book_results:
        print(f"Book {book_name} not found!")
        return []
    book_node = book_results[0][0] if isinstance(book_results[0], tuple) else book_results[0]
    return A.api.L.d(book_node, otype='word')

# Collect words from both books
print("Getting words from Samuel_I and Samuel_II...")
samuel1_words = get_book_words('Samuel_I')
samuel2_words = get_book_words('Samuel_II')
all_words = list(samuel1_words) + list(samuel2_words)
print(f"Total words: {len(all_words)}")

# Count proper nouns (persons)
# ETCBC uses 'nmpr' (nomen proprium) for proper nouns
# and 'nametype' feature can distinguish person names

name_counts = Counter()

for word in all_words:
    # Get part of speech
    sp = A.api.F.sp.v(word)

    # Check if it's a proper noun
    if sp == 'nmpr':
        # Get lemma (lexical form)
        lemma = A.api.F.lex.v(word)
        hebrew = A.api.F.voc_lex_utf8.v(word)

        # Store with Hebrew form
        name_counts[(lemma, hebrew)] += 1

print(f"\nFound {len(name_counts)} unique proper nouns")

# Get top 20 to see the full picture
print("\nTop 20 proper nouns in 1 & 2 Samuel:")
print("=" * 60)
for (lemma, hebrew), count in name_counts.most_common(20):
    try:
        print(f"{count:4d}  {hebrew:<15}  ({lemma})")
    except UnicodeEncodeError:
        print(f"{count:4d}  {lemma}")

# Now let's filter for person names specifically
# ETCBC has 'nametype' feature: 'pers' for persons, 'topo' for places, 'ppde' for peoples
print("\n" + "=" * 60)
print("Filtering for PERSON names only (nametype='pers'):")
print("=" * 60)

person_counts = Counter()

for word in all_words:
    sp = A.api.F.sp.v(word)

    if sp == 'nmpr':
        # Check if it's a person name
        nametype = A.api.F.nametype.v(word)
        if nametype == 'pers':
            lemma = A.api.F.lex.v(word)
            hebrew = A.api.F.voc_lex_utf8.v(word)
            person_counts[(lemma, hebrew)] += 1

print(f"\nFound {len(person_counts)} unique person names")

print("\nTOP 5 INDIVIDUALS IN 1 & 2 SAMUEL:")
print("=" * 60)
for rank, ((lemma, hebrew), count) in enumerate(person_counts.most_common(5), 1):
    try:
        print(f"{rank}. {hebrew:<15} - {count} occurrences")
    except UnicodeEncodeError:
        print(f"{rank}. {lemma} - {count} occurrences")

# Save results to file
output_file = "results/samuel_top_individuals_results.txt"
os.makedirs("results", exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("Top Individuals Mentioned in 1 & 2 Samuel\n")
    f.write("=" * 60 + "\n\n")
    f.write("Analysis using ETCBC BHSA (Text-Fabric)\n")
    f.write("Filtering for proper nouns with nametype='pers' (persons)\n\n")

    f.write("TOP 5 INDIVIDUALS:\n")
    f.write("-" * 40 + "\n")
    for rank, ((lemma, hebrew), count) in enumerate(person_counts.most_common(5), 1):
        f.write(f"{rank}. {hebrew} - {count} occurrences\n")

    f.write("\n\nFull list (Top 20 person names):\n")
    f.write("-" * 40 + "\n")
    for rank, ((lemma, hebrew), count) in enumerate(person_counts.most_common(20), 1):
        f.write(f"{rank:2d}. {hebrew:<15} ({lemma:<15}) - {count}\n")

print(f"\nResults saved to {output_file}")
