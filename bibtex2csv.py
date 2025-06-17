#!/usr/bin/env python3
"""
BibTeX to CSV Converter

This utility converts BibTeX files to CSV format with DOI and Title columns.
It uses bibtexparser for robust BibTeX file parsing and handles various
DOI formats, ensuring full DOI URLs in the output.

Features:
- Robust BibTeX parsing using bibtexparser library
- Converts DOIs to full URLs (https://doi.org/...)
- Handles missing titles and DOIs gracefully
- Outputs CSV with [DOI, Title] format
- Automatic output filename generation (.csv extension)
- Preserves text encoding and handles special characters

Requirements:
- Python 3.6+
- bibtexparser: pip install bibtexparser

Usage Examples:
    # Convert single BibTeX file
    python bibtex2csv.py bibfiles/ieee_search_string.bib

    # Convert with verbose output
    python bibtex2csv.py -v bibfiles/acm_search_string.bib

    # Convert multiple files
    python bibtex2csv.py bibfiles/*.bib

Input:
    BibTeX file with entries containing doi= and title= fields

Output:
    CSV file with columns:
    - DOI: Full URL format (https://doi.org/...)
    - Title: Paper title (cleaned of LaTeX commands)

Author: GitHub Copilot
Version: 1.0
"""

import argparse
import csv
import os
import re
import sys
from pathlib import Path
import bibtexparser


def clean_text(text):
    """Clean LaTeX commands and normalize text."""
    if not text:
        return ""
    
    # Remove LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def format_doi_url(doi):
    """Convert DOI to full URL format."""
    if not doi:
        return ""
    
    # Clean the DOI
    doi = doi.strip()
    
    # Remove existing URL prefixes if present
    if doi.startswith('https://doi.org/'):
        return doi
    elif doi.startswith('http://dx.doi.org/'):
        doi = doi[18:]
    elif doi.startswith('dx.doi.org/'):
        doi = doi[11:]
    
    # Add the standard URL prefix
    return f"https://doi.org/{doi}"


def convert_bibtex_to_csv(bibtex_path, verbose=False):
    """Convert BibTeX file to CSV with DOI and Title columns."""
    
    # Generate output filename
    input_path = Path(bibtex_path)
    output_path = input_path.with_suffix('.csv')
    
    if verbose:
        print(f"Converting: {bibtex_path}")
        print(f"Output: {output_path}")
    
    try:
        # Parse BibTeX file
        with open(bibtex_path, 'r', encoding='utf-8', errors='ignore') as f:
            bib_database = bibtexparser.load(f)
        
        if verbose:
            print(f"Found {len(bib_database.entries)} total BibTeX entries")
        
        # Process entries and collect data
        csv_data = []
        entries_with_doi = 0
        entries_with_title = 0
        valid_entries = 0
        
        for entry in bib_database.entries:
            doi = ""
            title = ""
            
            # Extract and format DOI
            if 'doi' in entry:
                doi = format_doi_url(entry['doi'])
                entries_with_doi += 1
            
            # Extract and clean title
            if 'title' in entry:
                title = clean_text(entry['title'])
                entries_with_title += 1
            elif 'booktitle' in entry:
                # Use booktitle as fallback
                title = clean_text(entry['booktitle'])
                entries_with_title += 1
            
            # Only include entries with at least one of DOI or title
            if doi or title:
                csv_data.append([doi, title])
                valid_entries += 1
        
        # Write CSV file
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['DOI', 'Title'])
            
            # Write data
            writer.writerows(csv_data)
        
        # Print summary
        print(f"Conversion completed: {bibtex_path}")
        print(f"  Total entries: {len(bib_database.entries)}")
        print(f"  Entries with DOI: {entries_with_doi}")
        print(f"  Entries with title: {entries_with_title}")
        print(f"  Valid entries exported: {valid_entries}")
        print(f"  Output saved to: {output_path}")
        
        if verbose and valid_entries > 0:
            print(f"\nSample entries:")
            for i, (doi, title) in enumerate(csv_data[:3], 1):
                print(f"  {i}. DOI: {doi}")
                print(f"     Title: {title[:80]}{'...' if len(title) > 80 else ''}")
        
        return True
        
    except Exception as e:
        print(f"Error converting {bibtex_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Convert BibTeX files to CSV format with DOI and Title columns')
    parser.add_argument('files', nargs='+', help='BibTeX file(s) to convert')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    # Process each file
    successful_conversions = 0
    total_files = len(args.files)
    
    for bibtex_file in args.files:
        if not os.path.exists(bibtex_file):
            print(f"Error: File '{bibtex_file}' not found.")
            continue
        
        if not bibtex_file.lower().endswith('.bib'):
            print(f"Warning: '{bibtex_file}' doesn't appear to be a BibTeX file (no .bib extension)")
        
        if convert_bibtex_to_csv(bibtex_file, args.verbose):
            successful_conversions += 1
        
        if total_files > 1:
            print()  # Add spacing between files
    
    # Final summary
    if total_files > 1:
        print(f"Conversion summary: {successful_conversions}/{total_files} files converted successfully")


if __name__ == "__main__":
    main()