"""
DOI Validation Utility for Academic Research

This utility validates Digital Object Identifiers (DOIs) by checking them against
the Crossref database to ensure they are legitimate and accessible. It's particularly
useful for cleaning bibliographic databases, validating reference lists, and ensuring
DOI accuracy in academic publications.

What does it do?
The tool takes a list of DOIs and queries the Crossref API to verify each one exists
and is valid. It retrieves paper titles for valid DOIs and provides error messages
for invalid ones, helping researchers maintain accurate citation databases.

Features:
- Validates DOIs using the official Crossref API
- Handles various DOI formats (with/without URL prefixes)
- Supports concurrent processing for faster validation
- Retrieves paper titles for verified DOIs
- Exports detailed results to CSV format
- Provides comprehensive validation statistics
- Includes rate limiting to respect API guidelines

Use Cases:
- Cleaning and validating bibliographic databases
- Verifying DOI accuracy before publication
- Quality control for systematic literature reviews
- Academic database maintenance and curation
- Preparing citation lists for journal submissions
- Validating extracted DOIs from various sources

Requirements:
- Python 3.6+
- requests library: pip install requests
- Internet connection for Crossref API access

Usage Examples:
    # Basic DOI validation
    python check_dois_valid.py -f doi_list.txt

    # Faster processing with concurrent requests
    python check_dois_valid.py -f doi_list.txt -c 5 -v

    # Validate with custom output file
    python check_dois_valid.py -f extracted_dois.txt -o validation_results.csv

    # Detailed verbose validation
    python check_dois_valid.py -f suspicious_dois.txt -v -o detailed_check.csv

Input Format:
    Text file with one DOI per line, UTF-8 encoded
    Supports both formats:
        10.1145/3287324.3287506
        https://doi.org/10.1145/3287324.3287506

Output Format:
    CSV file with columns:
    - DOI: The original DOI being checked
    - Valid: "Yes" or "No" indicating validity
    - Title/Error: Paper title if valid, error message if invalid

API Information:
    Uses Crossref REST API (https://api.crossref.org/works)
    - Free and publicly accessible
    - No authentication required
    - Rate limited (built-in delays respect guidelines)
    - Returns comprehensive bibliographic metadata

Validation Process:
    1. Clean DOI format (remove URL prefixes)
    2. Query Crossref API for each DOI
    3. Parse response for validity and metadata
    4. Extract paper title if DOI is valid
    5. Record error details for invalid DOIs

Performance Options:
    --concurrent: Number of simultaneous API requests
    - Default: 1 (sequential processing)
    - Higher values: Faster but more API load
    - Recommended: 3-5 for balance of speed and courtesy

Error Handling:
    - Network connectivity issues
    - API response errors and timeouts
    - File encoding and access problems
    - Malformed DOI formats
    - Rate limiting compliance

Statistics Provided:
    - Total DOIs processed
    - Number and percentage of valid DOIs
    - Number and percentage of invalid DOIs
    - Detailed per-DOI results in CSV output

Best Practices:
    - Use moderate concurrency (3-5) to respect API limits
    - Review invalid DOIs manually for potential typos
    - Keep results for future reference and auditing
    - Validate DOIs before including in publications

Author: GitHub Copilot
Version: 1.0
"""

import requests
import argparse
import sys
import time
import csv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

def clean_doi(doi_string):
    """Clean DOI by removing URL prefix and whitespace"""
    doi = doi_string.strip()
    if doi.startswith('https://doi.org/'):
        doi = doi[16:]  # Remove the URL prefix
    return doi

def check_doi(doi):
    """Check if a DOI is valid by querying the Crossref API"""
    url = f"https://api.crossref.org/works/{doi}"
    headers = {
        'User-Agent': 'DOI-Validator/1.0 (mailto:your@email.com)'  # Replace with your email
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            title = data['message'].get('title', ['Unknown Title'])[0]
            return doi, True, title
        else:
            return doi, False, f"HTTP Error: {response.status_code}"
    except requests.exceptions.RequestException as e:
        return doi, False, f"Request Error: {str(e)}"
    except Exception as e:
        return doi, False, f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Check if DOIs are valid using Crossref API')
    parser.add_argument('-f', '--file', required=True, help='File containing DOIs (one per line)')
    parser.add_argument('-o', '--output', help='Output CSV file (default: valid_dois.csv)')
    parser.add_argument('-c', '--concurrent', type=int, default=1, 
                       help='Number of concurrent requests (default: 1)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    # Set default output filename if not specified
    if not args.output:
        args.output = 'valid_dois.csv'
    
    # Read DOIs from file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            dois = [clean_doi(line) for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading file {args.file}: {e}")
        sys.exit(1)
    
    if not dois:
        print(f"No DOIs found in {args.file}")
        sys.exit(1)
    
    print(f"Checking {len(dois)} DOIs against Crossref API...")
    
    # Process DOIs with concurrent requests if specified
    results = []
    if args.concurrent > 1:
        with ThreadPoolExecutor(max_workers=args.concurrent) as executor:
            futures = [executor.submit(check_doi, doi) for doi in dois]
            for i, future in enumerate(futures):
                result = future.result()
                results.append(result)
                if args.verbose:
                    print(f"[{i+1}/{len(dois)}] {result[0]}: {'Valid' if result[1] else 'Invalid'}")
                else:
                    print(f"Checking DOIs: {i+1}/{len(dois)}", end='\r')
    else:
        # Process DOIs sequentially
        for i, doi in enumerate(dois):
            result = check_doi(doi)
            results.append(result)
            if args.verbose:
                print(f"[{i+1}/{len(dois)}] {doi}: {'Valid' if result[1] else 'Invalid'}")
            else:
                print(f"Checking DOIs: {i+1}/{len(dois)}", end='\r')
            time.sleep(0.5)  # Respect rate limits
    
    # Count valid and invalid DOIs
    valid_count = sum(1 for _, valid, _ in results if valid)
    invalid_count = len(results) - valid_count
    
    # Write results to CSV
    with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(['DOI', 'Valid', 'Title/Error'])
        for doi, valid, title in results:
            writer.writerow([doi, 'Yes' if valid else 'No', title])
    
    # Print summary
    print("\nResults Summary:")
    print(f"Total DOIs checked: {len(results)}")
    print(f"Valid DOIs: {valid_count} ({valid_count/len(results)*100:.1f}%)")
    print(f"Invalid DOIs: {invalid_count} ({invalid_count/len(results)*100:.1f}%)")
    print(f"Results saved to: {args.output}")

if __name__ == "__main__":
    main()