"""
Join multi-line verses in NASB text files so each verse is on a single line.
- Lines starting with a number are verse beginnings
- Lines starting with text (no number) are continuations of the previous verse
- Preserve chapter headers and their blank line spacing
"""

import os
import re

# Path to NASB books directory
books_dir = os.path.join('..', 'texts', 'nasb', 'books')

# Get all .txt files
txt_files = [f for f in os.listdir(books_dir) if f.endswith('.txt')]

print(f"Found {len(txt_files)} NASB text files to process")

for filename in txt_files:
    filepath = os.path.join(books_dir, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    joined_lines = []

    for line in lines:
        stripped = line.rstrip('\n')

        # Check if this is a chapter header
        is_chapter_header = re.match(r'^[A-Za-z0-9_ ]+ \d+ New American Standard Bible', stripped)

        # Check if this is a blank line
        is_blank = stripped.strip() == ''

        # Check if this is a verse start (begins with a number)
        is_verse_start = re.match(r'^\d+\s', stripped)

        if is_chapter_header or is_blank or is_verse_start:
            # These lines start fresh
            joined_lines.append(stripped)
        else:
            # This is a continuation line - join it to the previous line
            if joined_lines and joined_lines[-1].strip() != '':
                # Remove trailing space from previous line if present
                prev = joined_lines[-1].rstrip()
                # Join with a space, but clean up double spaces
                joined_lines[-1] = prev + ' ' + stripped.lstrip()
            else:
                # Edge case: continuation line with no previous content
                joined_lines.append(stripped)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(joined_lines))

    print(f"Processed {filename}")

print("\nAll files processed!")
