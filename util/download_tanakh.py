#!/usr/bin/env python3
"""
Download Hebrew Tanakh books from tanach.us with accents.
"""

import os
import time
import urllib.request
import urllib.parse

def download_tanakh_books():
    """Download all Tanakh books from tanach.us with Hebrew accents."""

    # Create output directory
    output_dir = "../texts/tanakh"
    os.makedirs(output_dir, exist_ok=True)

    # Complete list of Tanakh books with correct tanach.us naming
    tanakh_books = [
        # Torah (5 books)
        'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',

        # Nevi'im - Former Prophets (6 books)
        'Joshua', 'Judges', '1Samuel', '2Samuel', '1Kings', '2Kings',

        # Nevi'im - Latter Prophets (4 books)
        'Isaiah', 'Jeremiah', 'Ezekiel', 'Twelve',

        # Ketuvim (9 books)
        'Psalms', 'Proverbs', 'Job', 'SongofSongs', 'Ruth', 'Lamentations',
        'Ecclesiastes', 'Esther', 'Daniel', 'Ezra', 'Nehemiah', '1Chronicles', '2Chronicles'
    ]

    base_url = "https://www.tanach.us/Server.txt"

    successful_downloads = 0
    failed_downloads = []

    for book in tanakh_books:
        try:
            # Construct URL: Server.txt?BookName*&content=Accents
            params = f"{book}*&content=Accents"
            url = f"{base_url}?{params}"

            print(f"Downloading {book}...")

            # Download the content
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')

            # Skip if content is too short (likely an error)
            if len(content.strip()) < 100:
                print(f"Warning: {book} returned very short content, skipping")
                failed_downloads.append(book)
                continue

            # Save to file
            filename = f"{book.lower()}.txt"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[OK] Saved {book} to {filename}")
            successful_downloads += 1

            # Be respectful - small delay between requests
            time.sleep(0.5)

        except Exception as e:
            print(f"[FAIL] Failed to download {book}: {str(e)}")
            failed_downloads.append(book)
            continue

    print(f"\nDownload Summary:")
    print(f"Successful downloads: {successful_downloads}")
    print(f"Failed downloads: {len(failed_downloads)}")

    if failed_downloads:
        print(f"Failed books: {', '.join(failed_downloads)}")

    return successful_downloads, failed_downloads

def main():
    print("Downloading Hebrew Tanakh from tanach.us...")
    print("URL pattern: https://www.tanach.us/Server.txt?BookName*&content=Accents")
    print()

    successful, failed = download_tanakh_books()

    if successful > 0:
        print(f"\nDownloaded {successful} books to texts/tanakh/")

    if failed:
        print(f"\nNote: Some downloads failed. You may want to:")
        print("1. Check the book names against tanach.us documentation")
        print("2. Try downloading failed books manually")
        print("3. Check your internet connection")

if __name__ == "__main__":
    main()