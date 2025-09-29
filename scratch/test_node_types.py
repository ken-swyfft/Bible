#!/usr/bin/env python3
"""Test different node types and lexeme access"""

import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from tf.app import use

# Load dataset
A = use('etcbc/bhsa', silent=True)

if A and hasattr(A, 'api'):
    print("Testing node types and lexeme access...")

    # Check what node types exist
    print("Available node types:")
    try:
        node_types = A.api.TF.nodeTypes
        for otype in node_types:
            print(f"  {otype}")
    except Exception as e:
        print(f"Error getting node types: {e}")

    # Try different approaches to get lexeme data
    print(f"\nTesting different approaches:")

    # Approach 1: Get lexeme nodes directly
    try:
        lexeme_nodes = A.search('lex')
        print(f"Found {len(lexeme_nodes)} lexeme nodes")

        if lexeme_nodes:
            test_lex = lexeme_nodes[0]
            print(f"Testing lexeme node {test_lex}:")

            # Test features on lexeme nodes
            for feature in ['lex', 'g_lex_utf8', 'freq_lex']:
                try:
                    value = getattr(A.api.F, feature).v(test_lex)
                    print(f"  {feature}: '{value}'")
                except Exception as e:
                    print(f"  {feature}: ERROR - {e}")

    except Exception as e:
        print(f"Error with lexeme nodes: {e}")

    # Approach 2: Use different word access
    try:
        print(f"\nTesting word-to-lexeme relationships:")

        # Get words differently
        all_words = A.search('word')
        print(f"Total words in corpus: {len(all_words)}")

        if all_words:
            test_word = all_words[100]  # Try a different word
            print(f"Testing word {test_word}:")

            # Try using L (locality) to find related lexeme
            try:
                related_lexemes = A.api.L.u(test_word, 'lex')
                print(f"  Related lexemes: {related_lexemes}")

                if related_lexemes:
                    lex_node = related_lexemes[0]
                    lex_value = A.api.F.lex.v(lex_node)
                    print(f"  Lexeme value: '{lex_value}'")

            except Exception as e:
                print(f"  L.u error: {e}")

            # Try different feature combinations
            try:
                # Maybe the features work on different node types
                for feature in ['g_word_utf8', 'g_cons_utf8']:
                    value = getattr(A.api.F, feature).v(test_word)
                    if value:
                        print(f"  {feature}: '{value}' (SUCCESS!)")
                        break

            except Exception as e:
                print(f"  Feature test error: {e}")

    except Exception as e:
        print(f"Error with alternative word access: {e}")

    # Approach 3: Check specific Job words with context
    try:
        print(f"\nTesting Job words with more context:")
        job_words = A.search('book book=Iob\n<< word')

        if job_words:
            # Try multiple words to see if any work
            for i in [0, 100, 1000]:
                if i < len(job_words):
                    word = job_words[i]
                    g_word = A.api.F.g_word_utf8.v(word)
                    if g_word and g_word != 'None':
                        print(f"  Word {i}: '{g_word}' (found working word!)")
                        # Try to get its lexeme
                        try:
                            lex_nodes = A.api.L.u(word, 'lex')
                            if lex_nodes:
                                lex = A.api.F.lex.v(lex_nodes[0])
                                print(f"    Lexeme: '{lex}'")
                        except:
                            pass
                        break

    except Exception as e:
        print(f"Error with Job word testing: {e}")

else:
    print("Failed to load dataset")