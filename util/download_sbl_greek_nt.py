#!/usr/bin/env python3
"""
Download the SBL Greek New Testament (SBLGNT) text.
The SBLGNT is freely available under Creative Commons Attribution 4.0 license.
"""

import os
import urllib.request
import urllib.error

def create_output_directory():
    """Create the output directory if it doesn't exist."""
    output_dir = "../texts/greek_nt"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def download_sbl_greek_nt():
    """Download all SBL Greek New Testament books from GitHub."""
    output_dir = create_output_directory()

    # List of all New Testament books available in the SBLGNT repository
    books = [
        "Matt", "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph",
        "Phil", "Col", "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb",
        "Jas", "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev"
    ]

    base_url = "https://raw.githubusercontent.com/LogosBible/SBLGNT/master/data/sblgnt/text/"
    successful_downloads = 0
    failed_downloads = 0

    print(f"Downloading {len(books)} Greek NT books from SBLGNT repository...")

    for book in books:
        book_url = f"{base_url}{book}.txt"
        output_file = os.path.join(output_dir, f"{book.lower()}.txt")

        try:
            urllib.request.urlretrieve(book_url, output_file)
            print(f"[OK] Downloaded {book}")
            successful_downloads += 1
        except urllib.error.URLError as e:
            print(f"[FAIL] Could not download {book}: {e}")
            failed_downloads += 1

    print(f"\nDownload complete: {successful_downloads} successful, {failed_downloads} failed")
    return failed_downloads == 0

if __name__ == "__main__":
    success = download_sbl_greek_nt()
    if not success:
        print("\nAlternative: You can manually download the SBL Greek NT from:")
        print("https://sblgnt.com/download/")
        print("Save it as 'sbl_greek_nt.txt' in the texts/greek_nt/ directory")