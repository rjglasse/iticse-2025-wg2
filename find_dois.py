import requests
import time
import argparse
import sys
import csv

def find_doi(title):
    """Retrieve DOI for a given title using Crossref API."""
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