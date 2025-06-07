import argparse
import re
import sys
from pathlib import Path

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
    """Extract DOIs from a BibTeX file."""
    bibtex_dois = set()
    try:
        with open(bibtex_path, 'r', encoding='utf-8') as f:
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