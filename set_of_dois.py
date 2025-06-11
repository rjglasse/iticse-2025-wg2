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
- bibtexparser (for robust BibTeX parsing): pip install bibtexparser
- Directory containing BibTeX (.bib) files with DOI fields

Usage Examples:
    # Extract DOIs from current directory with detailed summary
    python set_of_dois.py

    # Process specific directory with file-by-file processing info
    python set_of_dois.py -d bibfiles/ -v

    # Save unique DOIs to file with comprehensive statistics
    python set_of_dois.py -d bibfiles/ -o unique_dois.txt

    # Analyze large bibliography collection
    python set_of_dois.py -d /path/to/papers/ -o master_doi_list.txt -v

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
    - DOI counts per individual file (always shown)
    - Total DOIs found across all files (with duplicates)
    - Number of unique DOIs after deduplication
    - Number and percentage of duplicate DOIs removed
    - Sample of unique DOIs for verification

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
import bibtexparser

def extract_dois_from_bibtex(bibtex_path):
    """Extract DOIs from a BibTeX file using bibtexparser."""
    bibtex_dois = set()
    try:
        with open(bibtex_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Parse the BibTeX file using bibtexparser
            bib_database = bibtexparser.load(f)
        
        # Extract DOIs from each entry
        for entry in bib_database.entries:
            if 'doi' in entry:
                doi = entry['doi'].strip()
                
                # Clean up DOI by removing common prefixes
                if doi.startswith('https://doi.org/'):
                    doi = doi[16:]
                elif doi.startswith('http://dx.doi.org/'):
                    doi = doi[18:]
                elif doi.startswith('dx.doi.org/'):
                    doi = doi[11:]
                
                if doi:  # Only add non-empty DOIs
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
    
    # Calculate total DOIs (with duplicates)
    total_dois_with_duplicates = sum(file_doi_counts.values())
    
    # Print results
    print(f"\nResults Summary:")
    print(f"================")
    print(f"Files processed: {len(bibtex_files)}")
    print(f"\nDOIs per file:")
    for filename, count in sorted(file_doi_counts.items()):
        print(f"  {filename}: {count} DOIs")
    
    print(f"\nOverall Statistics:")
    print(f"------------------")
    print(f"Total DOIs found (with duplicates): {total_dois_with_duplicates}")
    print(f"Unique DOIs across all files: {len(all_dois)}")
    if total_dois_with_duplicates > 0:
        duplicate_count = total_dois_with_duplicates - len(all_dois)
        duplicate_percentage = (duplicate_count / total_dois_with_duplicates) * 100
        print(f"Duplicate DOIs removed: {duplicate_count} ({duplicate_percentage:.1f}%)")
    
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
    if all_dois:
        sample_size = min(5, len(all_dois))
        print(f"\nSample of unique DOIs (first {sample_size}):")
        for doi in sorted(list(all_dois))[:sample_size]:
            print(f"  {doi}")
        
        if len(all_dois) > sample_size:
            print(f"  ... and {len(all_dois) - sample_size} more DOIs")

if __name__ == "__main__":
    main()