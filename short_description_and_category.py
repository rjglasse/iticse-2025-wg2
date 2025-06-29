"""
Paper Categorization and Description Tool

This tool uses OpenAI's API to automatically categorize academic papers and generate 
short descriptions based on their titles and abstracts. It extracts papers from 
BibTeX files based on a DOI list and outputs CSV with classifications and summaries.

Key Features:
- Filters BibTeX entries by DOI list
- Uses OpenAI GPT-4o for intelligent categorization
- Generates concise descriptions of paper contributions
- Handles missing abstracts gracefully
- Exports results to CSV with DOI, title, category, and description
- Includes error handling for API issues
- Respects API rate limits with built-in delays
- Provides progress tracking for datasets

Usage Examples:
    # Basic categorization and description
    python short_description_and_category.py --doi-file dois.txt -f papers.bib -o results.csv

    # With verbose output
    python short_description_and_category.py --doi-file dois.txt -f papers.bib -o results.csv -v

    # Use different model with custom delay
    python short_description_and_category.py --doi-file dois.txt -f papers.bib -o results.csv -m gpt-4 --delay 2.0

Requirements:
    - Python packages: openai, bibtexparser
    - OpenAI API key (set as OPENAI_API_KEY environment variable)
    - BibTeX files with title and preferably abstract fields
    - DOI list file (one DOI per line)

Author: Designed by Ric Glassey. Generated by GitHub Copilot for ITiCSE 2025 WG2 Systematic Literature Review
"""

import argparse
import re
import csv
import os
import time
from openai import OpenAI
import bibtexparser

def load_dois_from_file(dois_file):
    """Load DOIs from a text file (one DOI per line)."""
    dois = set()
    try:
        with open(dois_file, 'r', encoding='utf-8') as f:
            for line in f:
                doi = line.strip()
                if doi:
                    # Clean up DOI by removing common prefixes
                    if doi.startswith('https://doi.org/'):
                        doi = doi[16:]
                    elif doi.startswith('http://dx.doi.org/'):
                        doi = doi[18:]
                    elif doi.startswith('dx.doi.org/'):
                        doi = doi[11:]
                    dois.add(doi)
        print(f"Loaded {len(dois)} DOIs from filter file: {dois_file}")
        return dois
    except Exception as e:
        print(f"Error reading DOI filter file {dois_file}: {e}")
        return set()

def extract_papers_from_bibtex(bibtex_path, doi_filter):
    """Extract paper information from BibTeX file using bibtexparser."""
    papers = []
    
    try:
        with open(bibtex_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Parse the BibTeX file using bibtexparser
            bib_database = bibtexparser.load(f)
        
        print(f"Found {len(bib_database.entries)} total BibTeX entries")
        
        # Process each entry
        for entry in bib_database.entries:
            paper = {}
            
            # Extract DOI
            if 'doi' in entry:
                doi = entry['doi'].strip()
                # Clean up DOI by removing common prefixes
                if doi.startswith('https://doi.org/'):
                    doi = doi[16:]
                elif doi.startswith('http://dx.doi.org/'):
                    doi = doi[18:]
                elif doi.startswith('dx.doi.org/'):
                    doi = doi[11:]
                paper['doi'] = doi
            
            # Extract title (try title first, then booktitle as fallback)
            if 'title' in entry:
                title = clean_text(entry['title'])
                paper['title'] = title
            elif 'booktitle' in entry:
                title = clean_text(entry['booktitle'])
                paper['title'] = title
            
            # Extract abstract
            if 'abstract' in entry:
                abstract = clean_text(entry['abstract'])
                paper['abstract'] = abstract
            
            # Only include papers with at least title and DOI that match filter
            if paper.get('title') and paper.get('doi') and paper['doi'] in doi_filter:
                papers.append(paper)
        
        print(f"Found {len(papers)} papers matching DOI filter")
    
    except Exception as e:
        print(f"Error reading BibTeX file {bibtex_path}: {e}")
        return []
    
    return papers

def clean_text(text):
    """Clean LaTeX commands and normalize text."""
    # Remove LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def categorize_and_describe_paper(client, paper, model="gpt-4o"):
    """Categorize a paper and generate a short description using OpenAI API."""
    title = paper.get('title', 'No title')
    abstract = paper.get('abstract', 'No abstract available')
    
    # Create prompt for both category and description
    prompt = f"""Based on the title and abstract of this computer science paper, please provide:

1. CATEGORY: A specific computer science subject area or field (e.g., "Machine Learning", "Databases", "Software Engineering", "Computer Networks", "Operating Systems", "Computer Graphics", "Human-Computer Interaction", "Algorithms and Data Structures", "Programming Languages", "Distributed Systems", "Computer Security", "Theory of Computation", "Web Development", "Artificial Intelligence", etc.)

2. DESCRIPTION: A concise 1-2 sentence description of what the paper did/accomplished and its main contribution.

Title: {title}

Abstract: {abstract}

Please respond in this exact format:
CATEGORY: [Category Name]
DESCRIPTION: [Brief description of what was done and main contribution]"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert computer science researcher who categorizes papers and summarizes their contributions concisely."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.1
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse the response
        category = "Unknown Category"
        description = "No description available"
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('CATEGORY:'):
                category = line[9:].strip()
            elif line.startswith('DESCRIPTION:'):
                description = line[12:].strip()
        
        return category, description
        
    except Exception as e:
        print(f"Error analyzing paper '{title[:50]}...': {e}")
        return f"Error: {str(e)}", f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Categorize CS papers and generate descriptions using OpenAI')
    parser.add_argument('--doi-file', required=True, 
                       help='Text file containing DOIs to filter (one DOI per line)')
    parser.add_argument('-f', '--file', required=True, help='BibTeX file to analyze')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file')
    parser.add_argument('-m', '--model', default='gpt-4o', 
                       help='OpenAI model to use (default: gpt-4o)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed progress')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Delay between API calls in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        return
    
    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return
    
    # Check if input files exist
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        return
    
    if not os.path.exists(args.doi_file):
        print(f"Error: DOI filter file '{args.doi_file}' not found.")
        return
    
    # Load DOI filter
    doi_filter = load_dois_from_file(args.doi_file)
    if not doi_filter:
        print("Error: No valid DOIs found in filter file.")
        return
    
    print(f"Extracting papers from: {args.file}")
    print(f"Filtering by DOIs from: {args.doi_file}")
    
    # Extract papers from BibTeX
    papers = extract_papers_from_bibtex(args.file, doi_filter)
    if not papers:
        print("No papers matching DOI filter found.")
        return
    
    print(f"Processing {len(papers)} papers for categorization and description")
    print(f"Using model: {args.model}")
    
    # Process papers
    results = []
    start_time = time.time()
    
    for i, paper in enumerate(papers, 1):
        # Calculate progress metrics
        progress_percent = (i / len(papers)) * 100
        elapsed_time = time.time() - start_time
        if i > 1:  # Avoid division by zero
            avg_time_per_paper = elapsed_time / (i - 1)
            remaining_papers = len(papers) - i
            estimated_remaining = remaining_papers * avg_time_per_paper
            eta_minutes = int(estimated_remaining // 60)
            eta_seconds = int(estimated_remaining % 60)
            eta_str = f"{eta_minutes}m {eta_seconds}s"
        else:
            eta_str = "calculating..."
        
        if args.verbose:
            title_preview = paper['title'][:80] + "..." if len(paper['title']) > 80 else paper['title']
            print(f"[{i}/{len(papers)} - {progress_percent:.1f}%] {title_preview}")
            print(f"  ETA: {eta_str}")
        else:
            # Show compact progress for non-verbose mode
            print(f"Progress: {i}/{len(papers)} ({progress_percent:.1f}%) - ETA: {eta_str}", end='\r', flush=True)
        
        category, description = categorize_and_describe_paper(client, paper, args.model)
        
        results.append({
            'DOI': paper['doi'],
            'Title': paper['title'],
            'Category': category,
            'Description': description
        })
        
        if args.verbose:
            print(f"  Category: {category}")
            print(f"  Description: {description}")
            print()  # Add blank line for readability
        
        # Rate limiting
        if i < len(papers):  # Don't delay after the last paper
            time.sleep(args.delay)
    
    # Clear the progress line and show completion
    if not args.verbose:
        print()  # Move to new line after progress indicator
    
    total_time = time.time() - start_time
    total_minutes = int(total_time // 60)
    total_seconds = int(total_time % 60)
    print(f"Processing completed in {total_minutes}m {total_seconds}s")
    
    # Save results to CSV
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['DOI', 'Title', 'Category', 'Description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"\nResults saved to: {args.output}")
        
        # Show summary statistics
        from collections import Counter
        category_counts = Counter(result['Category'] for result in results)
        
        print(f"\nCategory Summary:")
        print("-" * 50)
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(results)) * 100
            print(f"{category}: {count} papers ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()