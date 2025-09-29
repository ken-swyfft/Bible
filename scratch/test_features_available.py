#!/usr/bin/env python3
"""Test what features are actually available and working"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from tf.app import use

# Load dataset
A = use('etcbc/bhsa', silent=True)

if A and hasattr(A, 'api'):
    print("Testing feature access...")

    # Get a few words from Job
    job_words = A.search('book book=Iob\n<< word')
    print(f"Found {len(job_words)} words in Job")

    if job_words:
        test_word = job_words[0]
        print(f"Testing features on word {test_word}:")

        # Test different lexeme-related features
        features_to_test = [
            'lex', 'g_lex', 'lex_utf8', 'g_lex_utf8',
            'g_word', 'g_word_utf8', 'voc_lex', 'voc_lex_utf8'
        ]

        for feature in features_to_test:
            try:
                if hasattr(A.api.F, feature):
                    value = getattr(A.api.F, feature).v(test_word)
                    print(f"  {feature}: '{value}' (type: {type(value)})")
                else:
                    print(f"  {feature}: FEATURE NOT AVAILABLE")
            except Exception as e:
                print(f"  {feature}: ERROR - {e}")

        # Test if we can get the text content directly
        print(f"\nTesting alternative text access:")
        try:
            # Use the show method to see what's actually there
            print("Using A.show():")
            A.show([test_word], extraFeatures=['lex', 'g_word_utf8'])
        except Exception as e:
            print(f"Show method error: {e}")

        # Check if the feature is loaded
        print(f"\nChecking loaded features:")
        if hasattr(A.api, 'TF'):
            loaded_features = list(A.api.TF.features.keys())
            print(f"Loaded features count: {len(loaded_features)}")
            lex_features = [f for f in loaded_features if 'lex' in f]
            print(f"Lexeme-related features: {lex_features}")

else:
    print("Failed to load dataset")