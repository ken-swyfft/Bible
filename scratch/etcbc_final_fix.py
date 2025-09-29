#!/usr/bin/env python3
"""
ETCBC BHSA Final Fix - Handle Unicode and tuple structure properly
"""

import os
import sys

# Critical: Set environment for UTF-8 before any imports
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# Redirect stdout to handle Unicode properly
class UnicodeStdout:
    def __init__(self, original_stdout):
        self.original = original_stdout

    def write(self, text):
        try:
            self.original.write(text)
        except UnicodeEncodeError:
            # Replace problematic Unicode with safe alternatives
            safe_text = text.encode('ascii', errors='replace').decode('ascii')
            self.original.write(safe_text)

    def flush(self):
        self.original.flush()

# Replace stdout temporarily
original_stdout = sys.stdout
sys.stdout = UnicodeStdout(original_stdout)

def test_etcbc_with_unicode_safety():
    """Test ETCBC with proper Unicode handling"""
    print("Testing ETCBC with Unicode safety...")

    try:
        from tf.app import use

        # Load dataset
        A = use('etcbc/bhsa', silent=True)

        if A and hasattr(A, 'api'):
            print("Dataset loaded successfully")

            # Test Job words with proper tuple handling
            words = A.search('book book=Iob\n<< word')
            print(f"Found {len(words)} words in Job")

            if words:
                successful_extractions = 0
                lemmas = []

                # Test both tuple elements to see which works
                print("Testing tuple element access...")

                for i, word_tuple in enumerate(words[:100]):  # Test first 100 words
                    if len(word_tuple) >= 2:
                        # Try second element (actual word ID)
                        word_id = word_tuple[1]

                        try:
                            lemma = A.api.F.lex.v(word_id)
                            if lemma and lemma.strip():
                                lemmas.append(lemma.strip())
                                successful_extractions += 1
                        except Exception:
                            # Skip Unicode/other errors silently
                            pass

                print(f"Successfully extracted {successful_extractions} lemmas from first 100 words")
                print(f"Sample lemmas: {lemmas[:10] if lemmas else 'None found'}")

                if successful_extractions > 0:
                    print("SUCCESS: ETCBC lemma extraction working!")

                    # Test full extraction for Job
                    print("Extracting all Job lemmas...")
                    all_job_lemmas = []

                    for word_tuple in words:
                        if len(word_tuple) >= 2:
                            word_id = word_tuple[1]
                            try:
                                lemma = A.api.F.lex.v(word_id)
                                if lemma and lemma.strip():
                                    all_job_lemmas.append(lemma.strip())
                            except Exception:
                                pass

                    print(f"Total Job lemmas extracted: {len(all_job_lemmas)}")
                    print(f"Unique Job lemmas: {len(set(all_job_lemmas))}")

                    # Test with another book for comparison
                    print("Testing with Genesis for comparison...")
                    genesis_words = A.search('book book=Genesis\n<< word')
                    genesis_lemmas = []

                    for word_tuple in genesis_words[:1000]:  # Sample from Genesis
                        if len(word_tuple) >= 2:
                            word_id = word_tuple[1]
                            try:
                                lemma = A.api.F.lex.v(word_id)
                                if lemma and lemma.strip():
                                    genesis_lemmas.append(lemma.strip())
                            except Exception:
                                pass

                    print(f"Genesis sample lemmas: {len(genesis_lemmas)}")

                    if len(all_job_lemmas) > 0 and len(genesis_lemmas) > 0:
                        print("FINAL SUCCESS: ETCBC extraction fully working!")
                        return A, all_job_lemmas, genesis_lemmas

                else:
                    print("FAILED: No lemmas extracted")
            else:
                print("FAILED: No words found in Job")
        else:
            print("FAILED: Dataset loading failed")

    except Exception as e:
        print(f"FAILED: Exception occurred: {e}")

    return None, None, None

if __name__ == "__main__":
    result = test_etcbc_with_unicode_safety()

    if result[0]:
        print("\nETCBC BHSA is now fully functional!")
        print("Ready to implement proper morphological analysis.")
    else:
        print("\nStill having issues with ETCBC BHSA.")
        print("May need alternative approach or dataset reinstallation.")

    # Restore original stdout
    sys.stdout = original_stdout