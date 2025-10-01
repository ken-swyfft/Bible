"""
Split multi-verse lines in NASB text files.

This script fixes NASB book files where multiple verses appear on a single line.
For example:
  6 "Text of verse 6... 7" Text of verse 7...

The script splits these into separate lines:
  6 "Text of verse 6...
  7" Text of verse 7...
"""

import os
import re

# Path to NASB books directory
books_dir = os.path.join('..', 'texts', 'nasb', 'books')

# Get all .txt files
txt_files = [f for f in os.listdir(books_dir) if f.endswith('.txt')]

print(f"Found {len(txt_files)} NASB text files to process")

total_splits = 0

for filename in txt_files:
    filepath = os.path.join(books_dir, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    splits_in_file = 0

    for line in lines:
        stripped = line.rstrip('\n')

        # Check if this is a verse line (starts with a number)
        verse_match = re.match(r'^(\d+)\s+(.+)$', stripped)

        if verse_match:
            verse_num = verse_match.group(1)
            verse_text = verse_match.group(2)

            # Look for additional verse numbers in the text
            # Pattern: space or punctuation + digit(s) + quote (single or double)
            # This catches patterns like " 7"", " 10'", ".25""
            split_pattern = r'[.\s](\d+)["\047]'

            # Find all matches
            matches = list(re.finditer(split_pattern, verse_text))

            if matches:
                # We have multiple verses on this line
                splits_in_file += 1

                # Split the line at each verse boundary
                last_pos = 0
                current_verse_num = verse_num

                for match in matches:
                    # Extract text up to this match
                    text_segment = verse_text[last_pos:match.start()].strip()

                    # Add the verse with its number
                    fixed_lines.append(f"{current_verse_num} {text_segment}")

                    # Update for next verse
                    current_verse_num = match.group(1)
                    last_pos = match.end() - 1  # Include the quote character

                # Add the final verse segment
                final_segment = verse_text[last_pos:].strip()
                if final_segment:
                    fixed_lines.append(f"{current_verse_num} {final_segment}")
            else:
                # Normal single verse line
                fixed_lines.append(stripped)
        else:
            # Not a verse line (chapter header, blank line, etc.)
            fixed_lines.append(stripped)

    if splits_in_file > 0:
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))

        print(f"Processed {filename}: split {splits_in_file} lines")
        total_splits += splits_in_file
    else:
        print(f"Processed {filename}: no splits needed")

print(f"\nAll files processed! Total splits: {total_splits}")
