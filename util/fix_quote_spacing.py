"""
Fix extra spaces after opening quotation marks in NASB verses.

This script removes the extra space that appears after verse numbers and opening
quotes in patterns like:
  7 " If you do well...
Should be:
  7 "If you do well...
"""

import os
import re

# Path to NASB books directory
books_dir = os.path.join('texts', 'nasb', 'books')

# Get all .txt files
txt_files = [f for f in os.listdir(books_dir) if f.endswith('.txt')]

print(f"Found {len(txt_files)} NASB text files to process")

total_fixes = 0

for filename in txt_files:
    filepath = os.path.join(books_dir, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix pattern: verse_number space quote space uppercase_letter
    # Replace with: verse_number space quote uppercase_letter
    fixed_content = re.sub(r'^(\d+) " ([A-Z])', r'\1 "\2', content, flags=re.MULTILINE)

    # Count how many fixes were made
    fixes_in_file = len(re.findall(r'^\d+ " [A-Z]', content, flags=re.MULTILINE))

    if fixes_in_file > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

        print(f"Processed {filename}: fixed {fixes_in_file} verses")
        total_fixes += fixes_in_file
    else:
        print(f"Processed {filename}: no fixes needed")

print(f"\nAll files processed! Total fixes: {total_fixes}")
