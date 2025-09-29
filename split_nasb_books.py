#!/usr/bin/env python3
"""
Split the NASB Bible text file into individual book files.
"""

import re
import os

def split_nasb_bible(input_file, output_dir):
    """
    Split the NASB Bible text into individual book files.
    Uses the complete Bible book list to ensure proper boundaries.

    Args:
        input_file: Path to the complete NASB Bible text file
        output_dir: Directory to save individual book files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the entire file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Complete list of Bible books in order (both Old and New Testament)
    bible_books = [
        'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
        'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel', '1 Kings', '2 Kings',
        '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther',
        'Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon',
        'Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel',
        'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah', 'Nahum',
        'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi',
        'Matthew', 'Mark', 'Luke', 'John', 'Acts',
        'Romans', '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
        'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
        '1 Timothy', '2 Timothy', 'Titus', 'Philemon',
        'Hebrews', 'James', '1 Peter', '2 Peter', '1 John', '2 John', '3 John',
        'Jude', 'Revelation'
    ]

    # Create patterns for each book (chapter 1 start)
    book_patterns = {}
    for book in bible_books:
        # Pattern: "BookName 1 New American Standard Bible"
        pattern = re.compile(rf'^{re.escape(book)} 1 New American Standard Bible', re.MULTILINE)
        book_patterns[book] = pattern

    # Find all book starting positions
    book_positions = []
    for book in bible_books:
        matches = list(book_patterns[book].finditer(content))
        if matches:
            # Take the first match for each book
            start_pos = matches[0].start()
            book_positions.append((start_pos, book))

    # Sort by position to maintain order
    book_positions.sort(key=lambda x: x[0])

    # Extract content for each book
    books_processed = 0
    for i, (start_pos, book_name) in enumerate(book_positions):
        # Determine end position (start of next book or end of file)
        if i + 1 < len(book_positions):
            end_pos = book_positions[i + 1][0]
        else:
            end_pos = len(content)

        # Extract book content
        book_content = content[start_pos:end_pos].strip()

        if book_content:
            save_book(book_name, book_content, output_dir)
            books_processed += 1
            print(f"Saved {book_name}")

    print(f"\nTotal books processed: {books_processed}")

    # Clean up any empty files
    cleanup_empty_files(output_dir)

def cleanup_empty_files(output_dir):
    """Remove any empty or nearly empty files."""
    for filename in os.listdir(output_dir):
        filepath = os.path.join(output_dir, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if len(content) < 50:  # Remove files with very little content
                os.remove(filepath)
                print(f"Removed empty file: {filename}")

def save_book(book_name, content, output_dir):
    """Save a book's content to a file."""
    # Clean up book name for filename (remove spaces, make lowercase, handle numbers)
    filename = book_name.lower().replace(' ', '_') + '.txt'
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    input_file = 'texts/nasb/_bible.txt'
    output_dir = 'texts/nasb/books'

    # Clean up existing files first
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)

    print(f"Splitting NASB Bible from {input_file}")
    print(f"Output directory: {output_dir}")

    split_nasb_bible(input_file, output_dir)
    print("Splitting complete!")

if __name__ == "__main__":
    main()