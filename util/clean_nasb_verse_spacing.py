"""
Clean up NASB text files to ensure consistent verse spacing.
- Remove blank lines between verses (so verses are separated by single newlines)
- Preserve blank lines between chapters
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
        content = f.read()

    # Replace multiple consecutive newlines with double newlines (preserve chapter breaks)
    # Then replace double newlines that aren't around chapter headers with single newlines

    # First, normalize all whitespace-only lines to actual blank lines
    content = re.sub(r'\n[ \t]+\n', '\n\n', content)

    # Replace 3+ consecutive newlines with exactly 2 (for chapter breaks)
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Now we need to identify chapter headers and preserve spacing around them
    # Chapter headers look like: "BookName N New American Standard Bible"
    lines = content.split('\n')

    cleaned_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this is a chapter header
        is_chapter_header = re.match(r'^[A-Za-z0-9_ ]+ \d+ New American Standard Bible', line.strip())

        if is_chapter_header:
            # Ensure blank line before chapter header (unless it's the first line)
            if cleaned_lines and cleaned_lines[-1] != '':
                cleaned_lines.append('')
            cleaned_lines.append(line)
            # Ensure blank line after chapter header
            if i + 1 < len(lines) and lines[i + 1].strip() != '':
                cleaned_lines.append('')
        elif line.strip() == '':
            # Only add blank line if previous line was a chapter header
            if cleaned_lines and re.match(r'^[A-Za-z0-9_ ]+ \d+ New American Standard Bible', cleaned_lines[-1].strip()):
                cleaned_lines.append(line)
            # Otherwise skip blank lines between verses
        else:
            # Regular verse line
            cleaned_lines.append(line)

        i += 1

    # Join lines and write back
    cleaned_content = '\n'.join(cleaned_lines)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f"Processed {filename}")

print("\nAll files processed!")
