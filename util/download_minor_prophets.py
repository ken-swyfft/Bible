#!/usr/bin/env python3
"""
Download the 12 Minor Prophets individually from tanach.us
"""

import os
import time
import urllib.request

def download_minor_prophets():
    """Download the 12 Minor Prophets individually."""

    output_dir = "../texts/tanakh"
    os.makedirs(output_dir, exist_ok=True)

    # The 12 Minor Prophets
    minor_prophets = [
        'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah', 'Micah',
        'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai', 'Zechariah', 'Malachi'
    ]

    base_url = "https://www.tanach.us/Server.txt"

    successful_downloads = 0
    failed_downloads = []

    for book in minor_prophets:
        try:
            # Construct URL
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

    print(f"\nMinor Prophets Download Summary:")
    print(f"Successful downloads: {successful_downloads}")
    print(f"Failed downloads: {len(failed_downloads)}")

    if failed_downloads:
        print(f"Failed books: {', '.join(failed_downloads)}")

if __name__ == "__main__":
    # First remove the incorrect "twelve.txt" file
    twelve_file = "../texts/tanakh/twelve.txt"
    if os.path.exists(twelve_file):
        os.remove(twelve_file)
        print("Removed incorrect twelve.txt file")

    download_minor_prophets()