#!/usr/bin/env python3
"""
Convert ESV markdown files to plain text format matching NASB structure.
"""

import os
import re

# Mapping of ESV filenames to NASB-style filenames
BOOK_NAME_MAP = {
    '01_Genesis.md': 'genesis.txt',
    '02_Exodus.md': 'exodus.txt',
    '03_Leviticus.md': 'leviticus.txt',
    '04_Numbers.md': 'numbers.txt',
    '05_Deuteronomy.md': 'deuteronomy.txt',
    '06_Joshua.md': 'joshua.txt',
    '07_Judges.md': 'judges.txt',
    '08_Ruth.md': 'ruth.txt',
    '09_I_Samuel.md': '1_samuel.txt',
    '10_II_Samuel.md': '2_samuel.txt',
    '11_I_Kings.md': '1_kings.txt',
    '12_II_Kings.md': '2_kings.txt',
    '13_I_Chronicles.md': '1_chronicles.txt',
    '14_II_Chronicles.md': '2_chronicles.txt',
    '15_Ezra.md': 'ezra.txt',
    '16_Nehemiah.md': 'nehemiah.txt',
    '17_Esther.md': 'esther.txt',
    '18_Job.md': 'job.txt',
    '19_Psalms.md': 'psalms.txt',
    '20_Proverbs.md': 'proverbs.txt',
    '21_Ecclesiastes.md': 'ecclesiastes.txt',
    '22_Song_of_Solomon.md': 'song_of_solomon.txt',
    '23_Isaiah.md': 'isaiah.txt',
    '24_Jeremiah.md': 'jeremiah.txt',
    '25_Lamentations.md': 'lamentations.txt',
    '26_Ezekiel.md': 'ezekiel.txt',
    '27_Daniel.md': 'daniel.txt',
    '28_Hosea.md': 'hosea.txt',
    '29_Joel.md': 'joel.txt',
    '30_Amos.md': 'amos.txt',
    '31_Obadiah.md': 'obadiah.txt',
    '32_Jonah.md': 'jonah.txt',
    '33_Micah.md': 'micah.txt',
    '34_Nahum.md': 'nahum.txt',
    '35_Habakkuk.md': 'habakkuk.txt',
    '36_Zephaniah.md': 'zephaniah.txt',
    '37_Haggai.md': 'haggai.txt',
    '38_Zechariah.md': 'zechariah.txt',
    '39_Malachi.md': 'malachi.txt',
    '40_Matthew.md': 'matthew.txt',
    '41_Mark.md': 'mark.txt',
    '42_Luke.md': 'luke.txt',
    '43_John.md': 'john.txt',
    '44_Acts.md': 'acts.txt',
    '45_Romans.md': 'romans.txt',
    '46_I_Corinthians.md': '1_corinthians.txt',
    '47_II_Corinthians.md': '2_corinthians.txt',
    '48_Galatians.md': 'galatians.txt',
    '49_Ephesians.md': 'ephesians.txt',
    '50_Philippians.md': 'philippians.txt',
    '51_Colossians.md': 'colossians.txt',
    '52_I_Thessalonians.md': '1_thessalonians.txt',
    '53_II_Thessalonians.md': '2_thessalonians.txt',
    '54_I_Timothy.md': '1_timothy.txt',
    '55_II_Timothy.md': '2_timothy.txt',
    '56_Titus.md': 'titus.txt',
    '57_Philemon.md': 'philemon.txt',
    '58_Hebrews.md': 'hebrews.txt',
    '59_James.md': 'james.txt',
    '60_I_Peter.md': '1_peter.txt',
    '61_II_Peter.md': '2_peter.txt',
    '62_I_John.md': '1_john.txt',
    '63_II_John.md': '2_john.txt',
    '64_III_John.md': '3_john.txt',
    '65_Jude.md': 'jude.txt',
    '66_Revelation_of_John.md': 'revelation.txt',
}

def convert_md_to_txt(md_file, txt_file):
    """Convert a markdown ESV file to plain text format matching NASB."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    output_lines = []
    current_chapter = 0
    book_name = None

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue

        # Extract book name from H1 heading (# Book Name)
        if line.startswith('# '):
            book_name = line[2:].strip()
            continue

        # Extract chapter number from H2 heading (## Chapter X)
        if line.startswith('## Chapter '):
            current_chapter = line[11:].strip()
            # Add blank line before chapter title (unless it's the first chapter)
            if output_lines:
                output_lines.append("")
            output_lines.append(f"{book_name} {current_chapter} English Standard Version")
            output_lines.append("")
            continue

        # Process verse lines (starting with number followed by period)
        match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if match and current_chapter:
            verse_num = match.group(1)
            verse_text = match.group(2)
            output_lines.append(f"{verse_num} {verse_text}")

    # Write to output file
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    print(f"Converted {os.path.basename(md_file)} -> {os.path.basename(txt_file)}")

def main():
    """Convert all ESV markdown files to plain text."""
    source_dir = 'texts/esv_temp/by_book'
    dest_dir = 'texts/esv/books'

    # Create destination directory
    os.makedirs(dest_dir, exist_ok=True)

    # Convert each file
    for md_filename, txt_filename in BOOK_NAME_MAP.items():
        md_path = os.path.join(source_dir, md_filename)
        txt_path = os.path.join(dest_dir, txt_filename)

        if os.path.exists(md_path):
            convert_md_to_txt(md_path, txt_path)
        else:
            print(f"Warning: {md_filename} not found")

    print(f"\nConversion complete! {len(BOOK_NAME_MAP)} books converted.")
    print(f"ESV text files saved to: {dest_dir}")

if __name__ == '__main__':
    main()
