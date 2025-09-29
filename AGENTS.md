##Purpose##
This is a project full of scripts that I use to analyze different aspects of Biblical texts, usually in the original languages.

By default, use Python.

Each top-level python script attempts to do one "analysis". It should output its results into `{scriptname}_results.txt`.

When reading static Hebrew texts for purposes of analysis, deduplicate ketiv/qere, keeping the qere.

Put scripts not used for analysis (for instance, for downloading or cleaning up static files) into the ./util/ directory.

When creating scripts to analyze a specific book, put the book name first, e.g., `proverbs_analyze_bicola.py`, or `proverbs_analyze_word_ratios.py`.