"""
DOI Overlap Analyzer for BibTeX Files

This utility compares DOIs from a reference list with DOIs found in BibTeX files
to identify overlaps and gaps in bibliographic coverage. It's particularly useful
for literature reviews, bibliography validation, and ensuring comprehensive 
citation coverage in academic research.

What does it do?
The tool takes two inputs: a list of target DOIs and a BibTeX file, then analyzes
how many of the target DOIs are present in the BibTeX collection. This helps
researchers understand the completeness of their bibliography and identify
missing papers that should be included.

Features:
- Extracts DOIs from plain text files and BibTeX entries
- Handles various DOI formats (with/without URL prefixes)
- Calculates overlap percentages and coverage statistics
- Identifies missing DOIs that need to be added
- Provides detailed verbose output for investigation
- Supports both console summary and detailed listings

Use Cases:
- Literature review completeness checking
- Bibliography validation for academic papers
- Conference proceedings coverage analysis
- Research corpus gap identification
- Citation database quality assessment
- Systematic review preparation and validation

Requirements:
- Python 3.6+
- bibtexparser (for robust BibTeX parsing): pip install bibtexparser
- Two input files: DOI list and BibTeX file

Usage Examples:
    # Basic overlap analysis
    python doi_overlap.py -d target_dois.txt -b my_bibliography.bib

    # Detailed analysis with missing DOI list
    python doi_overlap.py -d important_papers.txt -b conference.bib -v

    # Check literature review coverage
    python doi_overlap.py -d systematic_review_dois.txt -b collected_papers.bib -v

Input File Formats:
    DOI file: Plain text file with one DOI per line
    Example content:
        10.1145/3287324.3287506
        https://doi.org/10.1145/3304221.3319786
        10.1016/j.compedu.2019.103654

    BibTeX file: Standard .bib format with doi= fields
    Example entry:
        @article{smith2023,
          title={Paper Title},
          author={Smith, John},
          doi={10.1145/3287324.3287506},
          year={2023}
        }

Output Information:
    Console Summary:
    - Total DOIs in input list
    - Total DOIs found in BibTeX
    - Number and percentage of overlapping DOIs
    - Number and percentage of missing DOIs

    Verbose Output (with -v flag):
    - Complete list of DOIs found in BibTeX
    - Complete list of DOIs missing from BibTeX
    - Sorted alphabetically for easy review

Analysis Metrics:
    - Coverage Percentage: (Overlapping DOIs / Total Target DOIs) × 100
    - Gap Analysis: Shows which important papers are missing
    - Validation Results: Confirms bibliography completeness

Common Workflows:
    1. Systematic Review: Check if all identified papers are in your collection
    2. Conference Analysis: Verify proceedings coverage against known paper list
    3. Bibliography Audit: Ensure all cited works are properly included
    4. Research Gap Analysis: Find missing papers in your literature collection

Author: GitHub Copilot
Version: 1.0
"""

import argparse
import re
import sys
from pathlib import Path
import bibtexparser

def extract_dois_from_file(file_path):
    """Extract DOIs from a text file (one DOI per line)."""
    dois = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Strip whitespace and any potential URL prefixes
                line = line.strip()
                if line.startswith('https://doi.org/'):
                    line = line[16:]  # Remove the URL prefix
                if line:
                    dois.add(line)
    except Exception as e:
        print(f"Error reading DOI file {file_path}: {e}")
        sys.exit(1)
    
    return dois

def extract_dois_from_bibtex(bibtex_path):
    """Extract DOIs from a BibTeX file using bibtexparser."""
    bibtex_dois = set()
    try:
        with open(bibtex_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Parse the BibTeX file using bibtexparser
            bib_database = bibtexparser.load(f)
        
        print(f"Found {len(bib_database.entries)} total BibTeX entries")
        
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
        
        print(f"Found {len(bibtex_dois)} entries with valid DOI information")
        
    except Exception as e:
        print(f"Error reading BibTeX file {bibtex_path}: {e}")
        sys.exit(1)
    
    return bibtex_dois

def main():
    parser = argparse.ArgumentParser(description='Find overlap between DOIs and a BibTeX file')
    parser.add_argument('-d', '--doi-file', required=True, help='File containing DOIs (one per line)')
    parser.add_argument('-b', '--bibtex', required=True, help='BibTeX file to check for DOIs')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    # Extract DOIs from both files
    doi_list = extract_dois_from_file(args.doi_file)
    bibtex_dois = extract_dois_from_bibtex(args.bibtex)
    
    if not doi_list:
        print(f"No DOIs found in {args.doi_file}")
        sys.exit(1)
    
    if not bibtex_dois:
        print(f"No DOIs found in BibTeX file {args.bibtex}")
        sys.exit(1)
    
    # Find the overlap
    overlapping_dois = doi_list.intersection(bibtex_dois)
    missing_dois = doi_list - bibtex_dois
    
    # Calculate percentage
    overlap_percentage = (len(overlapping_dois) / len(doi_list)) * 100
    
    # Print results
    print(f"\nResults Summary:")
    print(f"----------------")
    print(f"DOIs in input file: {len(doi_list)}")
    print(f"DOIs in BibTeX file: {len(bibtex_dois)}")
    print(f"Overlapping DOIs: {len(overlapping_dois)} ({overlap_percentage:.1f}%)")
    print(f"Missing DOIs: {len(missing_dois)} ({100-overlap_percentage:.1f}%)")
    
    if args.verbose:
        if overlapping_dois:
            print("\nDOIs found in BibTeX:")
            print("---------------------")
            for doi in sorted(overlapping_dois):
                print(f"{doi}")
        
        if missing_dois:
            print("\nDOIs missing from BibTeX:")
            print("------------------------")
            for doi in sorted(missing_dois):
                print(f"{doi}")
    
if __name__ == "__main__":
    main()