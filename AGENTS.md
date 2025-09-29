## General notes ##
- This is a project full of scripts that I use to analyze different aspects of Biblical texts, usually in the original languages.
- By default, use Python.
- Each top-level python script attempts to do one "analysis". It should output its results into `{scriptname}_results.txt`.
- When creating scripts to analyze a specific book, put the book name first, e.g., `proverbs_analyze_bicola.py`, or `proverbs_analyze_word_ratios.py`.
- When reading static Hebrew texts for purposes of analysis, deduplicate ketiv/qere, keeping the qere.
- Put scripts not used for analysis (for instance, for downloading or cleaning up static files) into the ./util/ directory.
- Put debug, test, and experimental scripts into the ./scratch/ directory. This includes scripts used for testing APIs, debugging features, or exploring approaches that don't produce final analysis results.
- When creating an analysis script, ALWAYS add detailed comments at the top of the script explaining its purpose and how it goes about doing it. ALWAYS keep those comments up-to-date as you continue to update the script.

## Text Sources and Locations

### Hebrew Texts (Tanakh)
- Location: `./texts/tanakh/`
- Source: Westminster Leningrad Codex from tanach.us
- Format: UXLC (Unicode/XML Leningrad Codex) with cantillation marks
- Books: All 39 Hebrew Bible books in separate .txt files
- Naming: Lowercase, e.g., `genesis.txt`, `proverbs.txt`

### English Texts (NASB)
- Location: `./texts/nasb/books/`
- Source: New American Standard Bible
- Format: Plain text with verse numbers
- Books: All 66 Bible books in separate .txt files
- Naming: Lowercase, e.g., `genesis.txt`, `proverbs.txt`

### Greek New Testament
- Location: `./texts/greek_nt/`
- Source: SBL Greek New Testament (SBLGNT) from GitHub
- License: Creative Commons Attribution 4.0
- Format: Individual book files with verse references
- Books: All 27 NT books in separate .txt files
- Naming: Lowercase abbreviations, e.g., `matt.txt`, `1cor.txt`

## Text Processing Guidelines

### Hebrew Text Parsing
- Lines may contain Unicode directional marks - use regex to clean: `re.sub(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', line)`
- Verse pattern: `number ׃number hebrew_text` (e.g., "1 ׃1 מִשְׁלֵי...")
- Remove end punctuation: `re.sub(r'[׃פס]\s*$', '', text)`
- **IMPORTANT**: Treat maqqeph (־) separated words as separate words when counting
- Hebrew character range for filtering: `\u0590` to `\u05FF` (includes vowel points and cantillation)

### English Text Parsing
- Look for chapter headers: `Proverbs N New American Standard Bible`
- Verse pattern: `number verse_text`
- Word counting: Use `re.findall(r'\b\w+\b', text)` to handle punctuation properly

### Unicode Handling
- Hebrew text may cause encoding issues in Windows console
- Use try/except blocks when printing Hebrew text
- Save output files with UTF-8 encoding: `open(file, "w", encoding="utf-8")`

## Script Organization

### Utility Scripts
Location: `./util/`
- `download_tanakh.py` - Downloads Hebrew texts from tanach.us
- `download_minor_prophets.py` - Downloads 12 minor prophets individually
- `download_sbl_greek_nt.py` - Downloads SBL Greek NT from GitHub
- `split_nasb_books.py` - Splits NASB Bible into individual book files

All utility scripts are configured to work from the util/ directory with relative paths to parent directories.

### Debug/Test Scripts
Location: `./scratch/`
- Contains debug, test, and experimental scripts
- API testing scripts (e.g., Text-Fabric exploration)
- Feature debugging and exploration scripts
- Temporary scripts used during development
- Scripts that don't produce final analysis results

These scripts are kept separate from production analysis and utility scripts to maintain project organization.