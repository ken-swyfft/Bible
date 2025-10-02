#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test ketiv/qere handling"""
import re
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Test cases from Proverbs 2:7-8
test_verse_7 = "*וצפן **יִצְפֹּ֣ן לַ֭יְשָׁרִים תּוּשִׁיָּ֑ה מָ֝גֵ֗ן לְהֹ֣לְכֵי תֹֽם"
test_verse_8 = "לִ֭נְצֹר אָרְח֣וֹת מִשְׁפָּ֑ט וְדֶ֖רֶךְ *חסידו **חֲסִידָ֣יו יִשְׁמֹֽר"

try:
    print("Original verse 7:", test_verse_7)
    print("Original verse 8:", test_verse_8)
except:
    print("Original verse 7: [Hebrew text]")
    print("Original verse 8: [Hebrew text]")
print()

# Process ketiv/qere
def process_ketiv_qere(text):
    # Remove ketiv (marked with *word), keep qere (marked with **word)
    text = re.sub(r'\*\S+\s+\*\*', '**', text)  # Remove ketiv, leave qere marker
    text = re.sub(r'\*\*', '', text)  # Remove qere marker
    return text

processed_7 = process_ketiv_qere(test_verse_7)
processed_8 = process_ketiv_qere(test_verse_8)

try:
    print("Processed verse 7:", processed_7)
    print("Processed verse 8:", processed_8)
except:
    print("Processed verse 7: [Hebrew text]")
    print("Processed verse 8: [Hebrew text]")
print()

# Count words
def count_words(text):
    words = []
    for word_group in text.split():
        maqqeph_parts = word_group.split('־')
        for part in maqqeph_parts:
            if part.strip() and any('\u0590' <= c <= '\u05FF' for c in part):
                words.append(part.strip())
    return words

words_7_orig = count_words(test_verse_7)
words_7_proc = count_words(processed_7)
words_8_orig = count_words(test_verse_8)
words_8_proc = count_words(processed_8)

print(f"Verse 7 - Original count: {len(words_7_orig)}, Processed count: {len(words_7_proc)}")
print(f"  Difference: {len(words_7_orig) - len(words_7_proc)} (should be 1 for one ketiv removed)")
print(f"Verse 8 - Original count: {len(words_8_orig)}, Processed count: {len(words_8_proc)}")
print(f"  Difference: {len(words_8_orig) - len(words_8_proc)} (should be 1 for one ketiv removed)")
