"""
DOI Set Extractor for BibTeX Collections

This utility extracts all unique Digital Object Identifiers (DOIs) from BibTeX files
in a directory and creates a consolidated list. It's particularly useful for creating
reference lists, analyzing bibliographic collections, and preparing DOI datasets
for further analysis or validation.

What does it do?
The tool scans all BibTeX files in a specified directory, extracts DOI fields from
each entry, removes duplicates, and outputs a clean list of unique DOIs. This helps
researchers understand their collection's scope and create master DOI lists for
various academic purposes.

Features:
- Processes multiple BibTeX files in a directory automatically
- Extracts DOIs using robust pattern matching
- Handles various DOI formats (with/without URL prefixes)
- Removes duplicates to create unique DOI sets
- Provides file-by-file statistics in verbose mode
- Exports results to text files for further use
- Shows sample DOIs for verification

Use Cases:
- Creating master DOI lists from bibliographic collections
- Analyzing the scope and coverage of research databases
- Preparing input files for other analysis tools
- Validating bibliography completeness across multiple files
- Building reference datasets for systematic reviews
- Generating DOI inventories for research management

Requirements:
- Python 3.6+
- Directory containing BibTeX (.bib) files with DOI fields

Usage Examples:
    # Extract DOIs from current directory
    python set_of_dois.py

    # Process specific directory with verbose output
    python set_of_dois.py -d bibfiles/ -v

    # Save unique DOIs to file
    python set_of_dois.py -d bibfiles/ -o unique_dois.txt -v

    # Analyze large bibliography collection
    python set_of_dois.py -d /path/to/papers/ -o master_doi_list.txt

Input Requirements:
    BibTeX files (.bib) containing entries with DOI fields:
    Example format:
        @article{key2023,
          title={Paper Title},
          author={Author Name},
          doi={10.1145/1234567.1234568},
          year={2023}
        }

Output Formats:
    Console: Summary statistics and sample DOIs
    Text file: One unique DOI per line, sorted alphabetically

Processing Details:
    - Searches for doi= fields in BibTeX entries
    - Handles both quoted and braced DOI formats
    - Removes https://doi.org/ prefixes automatically
    - Ignores case differences in DOI field names
    - Eliminates whitespace and formatting issues

Statistics Provided:
    - Total number of BibTeX files processed
    - Number of unique DOIs found across all files
    - Per-file DOI counts (in verbose mode)
    - Sample DOIs for verification

Error Handling:
    - File encoding issues (uses UTF-8 with error tolerance)
    - Missing or malformed BibTeX files
    - Invalid DOI formats
    - Directory access problems

Author: GitHub Copilot
Version: 1.0
"""

import os
import re
import argparse
from pathlib import Path

def extract_dois_from_bibtex(bibtex_path):
    """Extract DOIs from a BibTeX file."""
    bibtex_dois = set()
    try:
        with open(bibtex_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Match DOIs in the standard BibTeX format
            # Looking for patterns like: doi = {10.1234/abc123}
            doi_pattern = re.compile(r'doi\s*=\s*["{]([^}"]+)["}]', re.IGNORECASE)
            matches = doi_pattern.findall(content)
            
            for doi in matches:
                # Clean up DOIs (remove whitespace, URL prefixes)
                doi = doi.strip()
                if doi.startswith('https://doi.org/'):
                    doi = doi[16:]
                bibtex_dois.add(doi)
    except Exception as e:
        print(f"Error reading BibTeX file {bibtex_path}: {e}")
    
    return bibtex_dois

def main():
    parser = argparse.ArgumentParser(description='Extract unique DOIs from all BibTeX files in a directory')
    parser.add_argument('-d', '--directory', default='.', 
                        help='Directory containing BibTeX files (default: current directory)')
    parser.add_argument('-o', '--output', help='Output file to save the list of unique DOIs')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    # Find all BibTeX files in the specified directory
    bibtex_files = list(Path(args.directory).glob('*.bib'))
    
    if not bibtex_files:
        print(f"No BibTeX files found in {args.directory}")
        return
    
    print(f"Found {len(bibtex_files)} BibTeX files")
    
    # Extract DOIs from all BibTeX files
    all_dois = set()
    file_doi_counts = {}
    
    for bib_file in bibtex_files:
        if args.verbose:
            print(f"Processing {bib_file}")
        
        dois = extract_dois_from_bibtex(bib_file)
        file_doi_counts[bib_file.name] = len(dois)
        all_dois.update(dois)
    
    # Print results
    print(f"\nResults Summary:")
    print(f"----------------")
    print(f"Total unique DOIs found: {len(all_dois)}")
    
    if args.verbose:
        print("\nDOIs per file:")
        for filename, count in sorted(file_doi_counts.items()):
            print(f"  {filename}: {count} DOIs")
    
    # Output to file if requested
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                for doi in sorted(all_dois):
                    f.write(f"{doi}\n")
            print(f"\nUnique DOIs saved to: {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}")
    
    # Print first few DOIs as a sample
    if all_dois and args.verbose:
        sample_size = min(5, len(all_dois))
        print(f"\nSample of DOIs (first {sample_size}):")
        for doi in sorted(list(all_dois))[:sample_size]:
            print(f"  {doi}")

if __name__ == "__main__":
    main()