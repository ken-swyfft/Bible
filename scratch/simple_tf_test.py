#!/usr/bin/env python3
"""Simple Text-Fabric test without Unicode issues"""

import os
import sys

# Set environment to handle Unicode properly
os.environ['PYTHONIOENCODING'] = 'utf-8'

from tf.core.api import TF

# Try direct TF approach instead of app
TF = TF()

# Load the BHSA dataset directly
result = TF.load('~/text-fabric-data/github/etcbc/bhsa/tf/2021', silent=True)

if result:
    print("Dataset loaded successfully!")

    # Test basic functionality
    F = TF.F  # Features
    L = TF.L  # Locality

    # Get some words
    words = list(TF.nodes())[TF.nodeRank['word'][0]:TF.nodeRank['word'][0]+10]
    print(f"First 10 word nodes: {words}")

    # Test features
    for word in words[:3]:
        lex = F.lex.v(word) if hasattr(F, 'lex') else None
        g_word = F.g_word_utf8.v(word) if hasattr(F, 'g_word_utf8') else None
        print(f"Word {word}: lex='{lex}', g_word='{g_word}'")

    # Test getting books
    book_nodes = list(TF.nodes())[TF.nodeRank['book'][0]:TF.nodeRank['book'][0]+5]
    print(f"First 5 book nodes: {book_nodes}")

    for book in book_nodes:
        book_name = F.book.v(book) if hasattr(F, 'book') else None
        print(f"Book {book}: '{book_name}'")

else:
    print("Failed to load dataset")