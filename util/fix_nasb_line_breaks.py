"""
Fix NASB verse line breaks.

This script cleans up NASB book files where some verses have been split across
multiple lines. It ensures each verse occupies exactly one line, making parsing
much easier.

The script:
1. Reads each NASB book file in ./texts/nasb/books/
2. Identifies verse beginnings (lines starting with a number followed by space)
3. Joins continuation lines (lines that don't start with a number) to the previous verse
4. Preserves blank lines between verses and chapter headers
5. Writes the fixed content back to each file
"""

import os
import re
from pathlib import Path

def fix_verse_line_breaks(file_path):
    """Fix line breaks in a single NASB book file."""
    print(f"Processing {file_path.name}...")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    current_verse = None

    for line in lines:
        line = line.rstrip('\n')

        # Check if this is a verse beginning (starts with a number)
        # or a chapter header (contains book name)
        if re.match(r'^\d+\s', line) or 'New American Standard Bible' in line:
            # If we have a pending verse, add it first
            if current_verse is not None:
                fixed_lines.append(current_verse)
                current_verse = None

            # Start a new verse
            current_verse = line
        elif line.strip() == '':
            # Empty line - add any pending verse first, then the blank line
            if current_verse is not None:
                fixed_lines.append(current_verse)
                current_verse = None
            fixed_lines.append('')
        else:
            # Continuation of current verse
            if current_verse is not None:
                current_verse += ' ' + line.strip()
            else:
                # Edge case: non-verse text without a pending verse
                fixed_lines.append(line)

    # Don't forget the last verse if there is one
    if current_verse is not None:
        fixed_lines.append(current_verse)

    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        for line in fixed_lines:
            f.write(line + '\n')

    print(f"  Fixed {file_path.name}")

def main():
    # Get the nasb books directory relative to util/
    script_dir = Path(__file__).parent
    nasb_dir = script_dir.parent / 'texts' / 'nasb' / 'books'

    if not nasb_dir.exists():
        print(f"Error: Directory {nasb_dir} does not exist")
        return

    # Process all .txt files in the directory
    book_files = sorted(nasb_dir.glob('*.txt'))

    if not book_files:
        print(f"No .txt files found in {nasb_dir}")
        return

    print(f"Found {len(book_files)} book files to process\n")

    for book_file in book_files:
        fix_verse_line_breaks(book_file)

    print(f"\nCompleted processing {len(book_files)} files")

if __name__ == '__main__':
    main()