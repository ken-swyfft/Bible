#!/usr/bin/env python3
"""
ETCBC BHSA TROUBLESHOOTING PLAN

This script implements a systematic approach to diagnosing and fixing
Text-Fabric ETCBC BHSA dataset issues.
"""

import os
import sys
from pathlib import Path

def step1_environment_setup():
    """Step 1: Fix environment and encoding issues"""
    print("="*60)
    print("STEP 1: ENVIRONMENT SETUP")
    print("="*60)

    # Set environment variables for proper Unicode handling
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'

    # For Windows, try to set console to UTF-8
    if sys.platform == 'win32':
        try:
            import subprocess
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
            print("✓ Set Windows console to UTF-8")
        except:
            print("⚠ Could not set console encoding")

    print("✓ Environment variables set")
    return True

def step2_data_location_check():
    """Step 2: Verify ETCBC data location and integrity"""
    print("\n" + "="*60)
    print("STEP 2: DATA LOCATION CHECK")
    print("="*60)

    # Check expected data locations
    home = Path.home()
    tf_data_path = home / 'text-fabric-data'
    bhsa_path = tf_data_path / 'github' / 'etcbc' / 'bhsa'

    print(f"Checking Text-Fabric data path: {tf_data_path}")
    print(f"  Exists: {tf_data_path.exists()}")

    if tf_data_path.exists():
        print(f"Contents: {list(tf_data_path.iterdir())}")

    print(f"\nChecking BHSA path: {bhsa_path}")
    print(f"  Exists: {bhsa_path.exists()}")

    if bhsa_path.exists():
        print(f"Contents: {list(bhsa_path.iterdir())}")

        # Check for TF data
        tf_path = bhsa_path / 'tf'
        if tf_path.exists():
            print(f"TF data: {list(tf_path.iterdir())}")

            # Check 2021 version specifically
            tf_2021 = tf_path / '2021'
            if tf_2021.exists():
                print(f"2021 data files: {len(list(tf_2021.iterdir()))} files")

                # Check for key features
                key_features = ['lex.tf', 'book.tf', 'g_word_utf8.tf']
                for feature in key_features:
                    feature_file = tf_2021 / feature
                    print(f"  {feature}: {feature_file.exists()}")
            else:
                print("⚠ 2021 version not found")
        else:
            print("⚠ TF directory not found")

    return bhsa_path.exists()

def step3_minimal_tf_test():
    """Step 3: Test minimal Text-Fabric loading"""
    print("\n" + "="*60)
    print("STEP 3: MINIMAL TEXT-FABRIC TEST")
    print("="*60)

    try:
        # Import Text-Fabric core
        from tf.fabric import Fabric
        print("✓ Text-Fabric core import successful")

        # Try direct Fabric loading
        home = Path.home()
        tf_path = str(home / 'text-fabric-data' / 'github' / 'etcbc' / 'bhsa' / 'tf' / '2021')

        print(f"Attempting to load from: {tf_path}")
        TF = Fabric(locations=[tf_path], silent=True)

        # Load minimal features
        api = TF.load('book lex g_word_utf8', silent=True)

        if api:
            print("✓ Minimal feature loading successful")
            print(f"✓ API object created: {type(api)}")

            # Test basic access
            try:
                # Get node counts
                print(f"Book nodes: {len(list(TF.search('book')))}")
                print(f"Word nodes: {len(list(TF.search('word')))}")

                # Test feature access
                books = list(TF.search('book'))
                if books:
                    first_book = books[0]
                    book_name = api.F.book.v(first_book)
                    print(f"First book name: '{book_name}'")

                    if book_name:
                        print("✓ Feature access working!")
                        return True
                    else:
                        print("⚠ Feature returns None")
                        return False
            except Exception as e:
                print(f"⚠ Error in feature access: {e}")
                return False
        else:
            print("⚠ API loading failed")
            return False

    except Exception as e:
        print(f"⚠ Text-Fabric import/loading error: {e}")
        return False

def step4_alternative_approaches():
    """Step 4: Try alternative access methods"""
    print("\n" + "="*60)
    print("STEP 4: ALTERNATIVE APPROACHES")
    print("="*60)

    # Approach 1: Use app with specific features
    print("Approach 1: App with specific features")
    try:
        from tf.app import use
        A = use('etcbc/bhsa', silent=True, features=['book', 'lex'])

        if A:
            print("✓ App loading with specific features successful")

            # Test search and feature access
            books = A.search('book')
            print(f"Found {len(books)} books")

            if books:
                test_book = books[0]
                try:
                    book_name = A.api.F.book.v(test_book)
                    print(f"Book name: '{book_name}'")

                    if book_name and book_name != 'None':
                        print("✓ Approach 1 working!")
                        return A
                except Exception as e:
                    print(f"Feature access error: {e}")
        else:
            print("⚠ App loading failed")
    except Exception as e:
        print(f"⚠ App approach error: {e}")

    # Approach 2: Direct TF with verbose output
    print("\nApproach 2: Direct TF with verbose output")
    try:
        from tf.fabric import Fabric

        home = Path.home()
        tf_path = str(home / 'text-fabric-data' / 'github' / 'etcbc' / 'bhsa' / 'tf' / '2021')

        TF = Fabric(locations=[tf_path])  # Not silent
        api = TF.load('')  # Load all features

        if api:
            print("✓ Full feature loading successful")
            return api
    except Exception as e:
        print(f"⚠ Direct TF approach error: {e}")

    return None

def step5_data_verification():
    """Step 5: Verify data integrity if we have a working connection"""
    print("\n" + "="*60)
    print("STEP 5: DATA VERIFICATION")
    print("="*60)

    # This step would be called if we get a working API from previous steps
    print("This step will be implemented once we have a working connection")
    return True

def run_full_diagnosis():
    """Run the complete troubleshooting sequence"""
    print("ETCBC BHSA TROUBLESHOOTING DIAGNOSIS")
    print("="*60)

    success = True

    # Step 1: Environment
    success &= step1_environment_setup()

    # Step 2: Data location
    success &= step2_data_location_check()

    if not success:
        print("\n❌ CRITICAL: Data not found. Need to reinstall or relocate ETCBC data.")
        return None

    # Step 3: Minimal test
    api = None
    if step3_minimal_tf_test():
        print("\n✅ SUCCESS: Minimal Text-Fabric working!")
    else:
        print("\n⚠ Minimal test failed, trying alternatives...")

        # Step 4: Alternative approaches
        api = step4_alternative_approaches()

        if api:
            print("\n✅ SUCCESS: Alternative approach working!")
        else:
            print("\n❌ FAILURE: All approaches failed")
            return None

    # Step 5: Data verification
    step5_data_verification()

    return api

if __name__ == "__main__":
    api = run_full_diagnosis()

    if api:
        print("\n" + "="*60)
        print("FINAL SUCCESS - READY FOR ANALYSIS")
        print("="*60)
        print("You now have a working ETCBC BHSA connection!")
        print("API object available for further testing.")
    else:
        print("\n" + "="*60)
        print("DIAGNOSIS COMPLETE - ISSUES IDENTIFIED")
        print("="*60)
        print("Specific problems have been identified.")
        print("Check the output above for next steps.")