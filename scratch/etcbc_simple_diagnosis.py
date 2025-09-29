#!/usr/bin/env python3
"""
ETCBC BHSA Simple Diagnosis (Windows-safe)
No Unicode symbols that cause console issues.
"""

import os
import sys
from pathlib import Path

def check_data_location():
    """Check if ETCBC data exists and is accessible"""
    print("CHECKING DATA LOCATION")
    print("-" * 40)

    home = Path.home()
    tf_data_path = home / 'text-fabric-data'
    bhsa_path = tf_data_path / 'github' / 'etcbc' / 'bhsa'

    print(f"Home directory: {home}")
    print(f"TF data path: {tf_data_path}")
    print(f"TF data exists: {tf_data_path.exists()}")

    if tf_data_path.exists():
        print("TF data contents:")
        for item in tf_data_path.iterdir():
            print(f"  {item.name}")

    print(f"\nBHSA path: {bhsa_path}")
    print(f"BHSA exists: {bhsa_path.exists()}")

    if bhsa_path.exists():
        print("BHSA contents:")
        for item in bhsa_path.iterdir():
            print(f"  {item.name}")

        # Check for TF files
        tf_path = bhsa_path / 'tf' / '2021'
        print(f"\nTF 2021 path: {tf_path}")
        print(f"TF 2021 exists: {tf_path.exists()}")

        if tf_path.exists():
            tf_files = list(tf_path.glob('*.tf'))
            print(f"TF files found: {len(tf_files)}")

            # Check key features
            key_features = ['lex.tf', 'book.tf', 'g_word_utf8.tf']
            for feature in key_features:
                feature_file = tf_path / feature
                exists = feature_file.exists()
                size = feature_file.stat().st_size if exists else 0
                print(f"  {feature}: exists={exists}, size={size}")

    return bhsa_path.exists()

def test_basic_tf_import():
    """Test basic Text-Fabric imports"""
    print("\nTESTING TEXT-FABRIC IMPORTS")
    print("-" * 40)

    try:
        import tf
        print(f"TF version: {tf.__version__ if hasattr(tf, '__version__') else 'unknown'}")
        print("TF import: SUCCESS")

        from tf.fabric import Fabric
        print("Fabric import: SUCCESS")

        from tf.app import use
        print("App import: SUCCESS")

        return True
    except Exception as e:
        print(f"Import error: {e}")
        return False

def test_direct_fabric_loading():
    """Test loading data directly with Fabric"""
    print("\nTESTING DIRECT FABRIC LOADING")
    print("-" * 40)

    try:
        from tf.fabric import Fabric

        home = Path.home()
        tf_path = str(home / 'text-fabric-data' / 'github' / 'etcbc' / 'bhsa' / 'tf' / '2021')

        print(f"Loading from: {tf_path}")

        # Try with minimal features and silent mode
        TF = Fabric(locations=[tf_path], silent=True)
        api = TF.load('book lex', silent=True)

        if api:
            print("Fabric loading: SUCCESS")
            print(f"API type: {type(api)}")

            # Test node access
            try:
                all_nodes = list(TF.nodes())
                print(f"Total nodes: {len(all_nodes)}")

                # Test search
                books = list(TF.search('book'))
                words = list(TF.search('word'))
                print(f"Books found: {len(books)}")
                print(f"Words found: {len(words)}")

                # Test feature access on a book
                if books:
                    first_book = books[0]
                    print(f"First book node: {first_book}")

                    book_name = api.F.book.v(first_book)
                    print(f"Book name: '{book_name}' (type: {type(book_name)})")

                    if book_name and book_name != 'None':
                        print("Feature access: SUCCESS!")
                        return api
                    else:
                        print("Feature access: FAILED - returns None")

            except Exception as e:
                print(f"Node/search error: {e}")

        else:
            print("Fabric loading: FAILED - no API returned")

    except Exception as e:
        print(f"Fabric loading error: {e}")

    return None

def test_app_loading():
    """Test loading with the app interface"""
    print("\nTESTING APP LOADING")
    print("-" * 40)

    try:
        # Set environment for UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'

        from tf.app import use

        # Try with silent mode to avoid Unicode console issues
        A = use('etcbc/bhsa', silent=True)

        if A and hasattr(A, 'api'):
            print("App loading: SUCCESS")
            print(f"App type: {type(A)}")

            # Test search
            try:
                books = A.search('book')
                print(f"Books found via app: {len(books)}")

                if books:
                    first_book = books[0]
                    book_name = A.api.F.book.v(first_book)
                    print(f"App book name: '{book_name}'")

                    if book_name and book_name != 'None':
                        print("App feature access: SUCCESS!")
                        return A
                    else:
                        print("App feature access: FAILED")

            except Exception as e:
                print(f"App search error: {e}")
        else:
            print("App loading: FAILED")

    except Exception as e:
        print(f"App loading error: {e}")

    return None

def run_diagnosis():
    """Run complete diagnosis"""
    print("ETCBC BHSA DIAGNOSIS")
    print("=" * 50)

    # Step 1: Check data
    data_ok = check_data_location()
    if not data_ok:
        print("\nCRITICAL: ETCBC data not found!")
        print("You may need to re-download the dataset.")
        return None

    # Step 2: Test imports
    import_ok = test_basic_tf_import()
    if not import_ok:
        print("\nCRITICAL: Text-Fabric import failed!")
        return None

    # Step 3: Test direct loading
    api = test_direct_fabric_loading()
    if api:
        print("\nSUCCESS: Direct Fabric loading works!")
        return api

    # Step 4: Test app loading
    app = test_app_loading()
    if app:
        print("\nSUCCESS: App loading works!")
        return app

    print("\nFAILED: All loading methods failed")
    print("Data exists but cannot be accessed properly")
    return None

if __name__ == "__main__":
    result = run_diagnosis()

    if result:
        print(f"\nFINAL RESULT: Working ETCBC connection established!")
        print("You can proceed with analysis using this connection.")
    else:
        print(f"\nFINAL RESULT: No working connection found.")
        print("Further investigation needed.")