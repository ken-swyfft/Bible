## General notes ##
- This is a project full of scripts that I use to analyze different aspects of Biblical texts, usually in the original languages.
- By default, use Python.
- Each top-level python script attempts to do one "analysis". It should output its results into `results/{scriptname}_results.txt`.
- When creating scripts to analyze a specific book, put the book name first, e.g., `proverbs_analyze_bicola.py`, or `proverbs_analyze_word_ratios.py`.
- When reading static Hebrew texts for purposes of analysis, deduplicate ketiv/qere, keeping the qere.
- Put scripts not used for analysis (for instance, for downloading or cleaning up static files) into the ./util/ directory.
- Put debug, test, and experimental scripts into the ./scratch/ directory. This includes scripts used for testing APIs, debugging features, or exploring approaches that don't produce final analysis results.
- When creating an analysis script, ALWAYS add detailed comments at the top of the script explaining its purpose and how it goes about doing it. ALWAYS keep those comments up-to-date as you continue to update the script.
- You are not as smart as you think you are, and the world (even just of Biblical texts and parsers) is far more complicated than you imagine. When approaching a task of any complexity, break the task down into as many small pieces as possible, then implement and test each individual step. Don't try to write a whole script at once: build it slowly, testing each step as you go.
- Corollary: Write your code in such a way that it's easy to test the individual parts.

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

## ETCBC BHSA API (Text-Fabric)

### Loading the Dataset
```python
from tf.app import use
A = use('etcbc/bhsa', silent=True)
```
- The BHSA (Biblia Hebraica Stuttgartensia Amstelodamensis) provides scholarly linguistic annotations
- Text-Fabric loads as an API object with `.api` attribute for accessing nodes and features

### Node Access and Navigation

#### Finding Books
```python
# Get all books
book_results = A.search('book')

# Get specific book (note: ETCBC uses specific naming)
book_results = A.search('book book=Iob')  # Job is named 'Iob'

# Extract node from result tuple
book_node = book_results[0][0] if isinstance(book_results[0], tuple) else book_results[0]

# Get book name from node
book_name = A.api.F.book.v(book_id)
```

#### Getting Words from a Book
**CRITICAL**: Use `L.d()` for downward edge traversal - NOT search with `<<` operator
```python
# CORRECT way - uses downward edges, no duplicates
word_nodes = A.api.L.d(book_node, otype='word')

# WRONG - causes ~14x duplication due to Cartesian product
# word_nodes = A.search('book book=X\n<< word')  # DO NOT USE
```

**Bug discovered in job_rare_vocabulary_etcbc.py**: Using `A.search('book book=X\n<< word')` returns each word approximately 14 times due to the relational query creating a Cartesian product. This caused massive overcounting (0 rare words found vs. the correct 650). Always use `L.d()` for traversing from book to words.

### Accessing Features
```python
# Get transliterated lemma (morphological base form)
lemma = A.api.F.lex.v(word_id)

# Get Hebrew vocalized text
hebrew = A.api.F.voc_lex_utf8.v(word_id)

# Get book name
book_name = A.api.F.book.v(book_id)
```

### Common Features
- `lex` - Transliterated lemma (lexical form)
- `voc_lex_utf8` - Hebrew vocalized lemma
- `book` - Book name
- `g_word_utf8` - Full word form with vocalization
- `sp` - Part of speech

### ETCBC Book Names
ETCBC uses specific naming conventions that differ from common English names:
- Job = 'Iob'
- Other books may have Latin-style names
- Always verify book names by querying: `A.search('book')` and inspecting results

### Windows Unicode Handling
When working with Hebrew text on Windows, always include:
```python
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# SafeUnicodeHandler for console output
class SafeUnicodeHandler:
    def safe_print(self, text):
        try:
            print(text)
        except UnicodeEncodeError:
            safe_text = str(text).encode('ascii', errors='replace').decode('ascii')
            print(safe_text)
```

### Error Handling Best Practices
- Wrap ETCBC operations in try/except blocks
- Node access can fail if features aren't available
- Skip individual word errors silently when processing large datasets
- Validate that dataset loaded successfully before proceeding

### Example Reference Script
See `job_rare_vocabulary_etcbc.py` for a complete working example demonstrating:
- Proper dataset loading
- Book and word node traversal
- Feature access (lex, voc_lex_utf8)
- Hebrew-to-transliteration mapping
- Windows Unicode handling
- Avoiding the L.d() vs search bug

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