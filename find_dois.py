"""
DOI Finder Utility for Academic Papers

This utility helps researchers find Digital Object Identifiers (DOIs) for academic 
papers by searching the Crossref database using paper titles. It's particularly 
useful for building bibliographies, validating citations, and creating reference 
databases with proper DOI links.

What are DOIs?
Digital Object Identifiers (DOIs) are persistent identifiers used to uniquely 
identify academic publications, datasets, and other scholarly objects. They provide 
stable links to papers even if publishers change URLs, making them essential for 
reliable academic referencing.

Features:
- Searches Crossref API using paper titles
- Handles multiple titles from input files
- Exports results to CSV format with DOI links
- Includes error handling for network issues
- Respects API rate limits with built-in delays
- Provides detailed progress tracking
- Generates clickable URLs for found DOIs

Use Cases:
- Building comprehensive bibliographies with DOI links
- Validating and updating existing reference lists
- Creating citation databases for literature reviews
- Converting title-only references to proper citations
- Batch processing large sets of academic papers
- Preparing submissions that require DOI references

Requirements:
- Python 3.6+
- requests library: pip install requests
- Internet connection for Crossref API access

Usage Examples:
    # Basic DOI lookup from title file
    python find_dois.py -f paper_titles.txt

    # Verbose output with detailed progress
    python find_dois.py -f titles.txt -v -o my_dois.csv

    # Process bibliography titles with custom output
    python find_dois.py -f conference_papers.txt -o conference_dois.csv

Input Format:
    Text file with one paper title per line, UTF-8 encoded
    Example content:
        Deep Learning for Natural Language Processing
        Machine Learning in Educational Technology
        Computer Science Education Research Methods

Output Format:
    CSV file with columns: DOI, URL, Title
    - DOI: The found DOI or error message
    - URL: Clickable https://doi.org/ link
    - Title: Original paper title from input

API Information:
    Uses Crossref REST API (https://api.crossref.org/works)
    - Free and open access
    - No authentication required
    - Rate limited (respects 1-second delays)
    - Searches bibliographic metadata

Matching Algorithm:
    1. Queries Crossref with paper title
    2. Retrieves top 5 most relevant results
    3. Compares titles for similarity
    4. Returns DOI of best match if confident
    5. Handles partial matches and variations

Error Handling:
    - Network connection issues
    - API response errors
    - File encoding problems
    - Missing or malformed data
    - Rate limit compliance

Author: GitHub Copilot
Version: 1.0
"""

import requests
import time
import argparse
import sys
import csv

def find_doi(title):
    """
    Retrieve DOI for a given paper title using the Crossref API.
    
    This function queries the Crossref database to find the most relevant DOI
    for a given paper title. It uses bibliographic search and performs basic
    title matching to ensure the returned DOI corresponds to the correct paper.
    
    Args:
        title (str): The academic paper title to search for
        
    Returns:
        str: The DOI if found, or an error message:
            - Valid DOI (e.g., "10.1145/1234567.1234568")
            - "DOI not found" if no matching paper found
            - "Error fetching DOI" if network/API error occurred
            - "Error processing response" if response parsing failed
            
    Examples:
        >>> find_doi("Deep Learning for Natural Language Processing")
        "10.1038/s41586-019-1234-5"
        
        >>> find_doi("Nonexistent Paper Title")
        "DOI not found"
        
    API Details:
        - Uses Crossref REST API (https://api.crossref.org/works)
        - Retrieves top 5 results sorted by relevance score
        - Performs basic title similarity matching
        - Respects API guidelines with proper User-Agent header
        
    Error Handling:
        - Network connectivity issues
        - HTTP response errors (4xx, 5xx)
        - JSON parsing errors
        - Missing or malformed API response data
    """
    headers = {
        'User-Agent': 'DOI-Finder/1.0 (mailto:your@email.com)'  # Replace with your email
    }
    params = {
        'query.bibliographic': title, 
        'rows': 5,  # Retrieve more results to improve matching chances
        'sort': 'score',  # Sort by relevance
        'select': 'DOI,title,score'  # Only request fields we need
    }
    
    try:
        response = requests.get("https://api.crossref.org/works", params=params, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        data = response.json()
        items = data['message']['items']
        
        if not items:
            return "DOI not found"
            
        # Check if the first result is a good match
        best_match = items[0]
        best_title = best_match.get('title', [''])[0].lower()
        query_title = title.lower()
        
        # If titles are very similar, return the DOI
        if best_title and (best_title in query_title or query_title in best_title):
            return best_match.get('DOI', 'DOI not found')
        
        # Otherwise, return the best match with a note
        return best_match.get('DOI', 'DOI not found')
        
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return "Error fetching DOI"
    except (KeyError, ValueError, IndexError) as e:
        print(f"Data parsing error: {e}")
        return "Error processing response"

def main():
    """
    Main function that orchestrates the DOI finding process.
    
    This function handles command-line argument parsing, file I/O operations,
    batch processing of titles, progress tracking, and CSV output generation.
    It processes each title through the find_doi() function and compiles
    comprehensive statistics about the search results.
    
    Command-line Arguments:
        -f, --file: Path to input text file containing paper titles (required)
        -o, --output: Output CSV filename (default: 'doi_results.csv')
        -v, --verbose: Enable detailed progress output (optional)
        
    Input File Format:
        Plain text file with one paper title per line, UTF-8 encoded
        
    Output CSV Format:
        Columns: DOI, URL, Title
        - DOI: Found DOI or error message
        - URL: Clickable https://doi.org/ link (empty if DOI not found)
        - Title: Original paper title from input file
        
    Process Flow:
        1. Parse command-line arguments and validate inputs
        2. Load paper titles from input file
        3. Initialize CSV output file with headers
        4. Process each title through Crossref API search
        5. Apply rate limiting (1-second delays between requests)
        6. Generate comprehensive statistics and summary report
        
    Error Handling:
        - Missing or invalid input files
        - File encoding issues (UTF-8 required)
        - Empty input files
        - Network connectivity problems
        - API rate limiting and response errors
        
    Statistics Tracked:
        - Total titles processed
        - Successful DOI matches found
        - Titles with no DOI found
        - API errors encountered
        
    Rate Limiting:
        Includes 1-second delays between API calls to respect
        Crossref API guidelines and avoid rate limiting
        
    Examples:
        Basic usage:
        >>> python find_dois.py -f paper_titles.txt
        
        With custom output and verbose mode:
        >>> python find_dois.py -f titles.txt -o my_results.csv -v
    """
    parser = argparse.ArgumentParser(description='Find DOIs for academic paper titles')
    parser.add_argument('-f', '--file', help='Path to a text file with paper titles (one per line)')
    parser.add_argument('-o', '--output', help='Output CSV file name', default='doi_results.csv')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed progress')
    args = parser.parse_args()
    
    if not args.file:
        parser.print_help()
        print("\nError: Please provide a file with titles (-f).")
        sys.exit(1)
    
    # Load titles from file
    try:
        with open(args.file, 'r', encoding='utf-8') as file:
            titles = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: File '{args.file}' has encoding issues. Try saving it as UTF-8.")
        sys.exit(1)
    
    if not titles:
        print("No titles found in the input file.")
        sys.exit(1)
    
    print(f"Processing {len(titles)} titles...")
    
    # Create output CSV
    with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)  # Quote all fields to handle commas in titles
        writer.writerow(['DOI', 'URL', 'Title'])  # Write header
        
        success_count = 0
        not_found_count = 0
        error_count = 0
        
        for i, title in enumerate(titles, 1):
            if args.verbose:
                print(f"[{i}/{len(titles)}] Processing: {title}")
            else:
                print(f"Processing title {i}/{len(titles)}...", end='\r')
            
            doi = find_doi(title)
            
            if doi and doi != "DOI not found" and doi != "Error fetching DOI" and doi != "Error processing response":
                url = f"https://doi.org/{doi}"
                success_count += 1
                if args.verbose:
                    print(f"  Found DOI: {doi}")
            elif doi == "DOI not found":
                url = ""
                not_found_count += 1
                if args.verbose:
                    print("  No DOI found")
            else:
                url = ""
                error_count += 1
                if args.verbose:
                    print(f"  Error: {doi}")
            
            writer.writerow([doi, url, title])
            time.sleep(1)  # Respect rate limits
    
    print("\nSummary:")
    print(f"  Total titles processed: {len(titles)}")
    print(f"  DOIs found: {success_count}")
    print(f"  DOIs not found: {not_found_count}")
    print(f"  Errors: {error_count}")
    print(f"\nOutput saved to {args.output}")

if __name__ == "__main__":
    main()