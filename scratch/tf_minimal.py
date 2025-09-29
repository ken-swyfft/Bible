#!/usr/bin/env python3
"""Minimal Text-Fabric approach"""

import os
import sys

# Set environment variables for proper Unicode handling
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    from tf.fabric import Fabric

    # Load the dataset with minimal features
    TF = Fabric(locations=['~/text-fabric-data/github/etcbc/bhsa/tf/2021'], silent=True)
    api = TF.load('')

    if api:
        print("Dataset loaded with minimal approach!")

        # Test basic access
        F = api.F
        L = api.L

        # Get word count
        word_nodes = list(api.nodes())[api.nodeRank['word'][0]:api.nodeRank['word'][0]+5]
        print(f"First 5 words: {word_nodes}")

        # Test features
        for word in word_nodes:
            try:
                lex = F.lex.v(word)
                print(f"Word {word}: lexeme='{lex}'")
                break  # Just test one
            except Exception as e:
                print(f"Error accessing lexeme: {e}")

    else:
        print("Failed to load API")

except Exception as e:
    print(f"Error loading Text-Fabric: {e}")
    print("Let's try a completely different approach...")

    # Alternative: Try without full app loading
    try:
        from tf.app import use

        # Try with silent and minimal features
        A = use('etcbc/bhsa', silent=True, load=['lex', 'book', 'g_word_utf8'])

        if A:
            print("Loaded with minimal features!")
        else:
            print("Failed to load minimal features")

    except Exception as e2:
        print(f"Alternative approach also failed: {e2}")

        # Final fallback - just check if we can import and get help
        try:
            from tf.app import use
            print("Text-Fabric import successful")
            print("Dataset location should be: ~/text-fabric-data/github/etcbc/bhsa/")

            # Check if data exists
            import pathlib
            home = pathlib.Path.home()
            data_path = home / 'text-fabric-data' / 'github' / 'etcbc' / 'bhsa'
            print(f"Checking data path: {data_path}")
            print(f"Data path exists: {data_path.exists()}")

            if data_path.exists():
                print("Contents:")
                for item in data_path.iterdir():
                    print(f"  {item.name}")

        except Exception as e3:
            print(f"Final check failed: {e3}")