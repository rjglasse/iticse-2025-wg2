"""
Subject Classification Utility for Computer Science Papers

This utility uses OpenAI's API to automatically classify academic papers into 
computer science course subjects based on their titles and abstracts. It's 
particularly useful for organizing large collections of papers, understanding 
research distributions, and preparing course-specific reading lists.

What does it do?
The tool extracts titles and abstracts from BibTeX files, sends them to OpenAI's 
API for classification, and outputs a CSV with DOIs, titles, and predicted 
computer science courses. This helps researchers quickly categorize papers 
into academic subject areas.

Features:
- Extracts text from BibTeX titles and abstracts
- Uses OpenAI GPT models for intelligent classification
- Handles missing abstracts gracefully
- Exports results to CSV with DOI, title, and predicted course
- Includes error handling for API issues
- Respects API rate limits with built-in delays
- Provides progress tracking for large datasets

Use Cases:
- Organizing research papers by academic subject
- Building course-specific reading lists
- Analyzing research distribution across CS fields
- Preparing literature reviews by subject area
- Academic database categorization and tagging
- Understanding research focus in conference proceedings

Requirements:
- Python 3.6+
- openai library: pip install openai
- OpenAI API key (set as environment variable OPENAI_API_KEY)
- BibTeX files with title and preferably abstract fields

Usage Examples:
    # Basic subject classification
    python subject_vibe.py -f papers.bib -o classifications.csv

    # Classify with verbose output
    python subject_vibe.py -f bibfiles/acm_chatgpt.bib -v -o cs_subjects.csv

    # Use specific OpenAI model
    python subject_vibe.py -f papers.bib -m gpt-4 -o detailed_analysis.csv

Environment Setup:
    export OPENAI_API_KEY="your-api-key-here"
    
    Or create a .env file:
    OPENAI_API_KEY=your-api-key-here

Input Requirements:
    BibTeX file with entries containing:
    - title= fields (required)
    - abstract= fields (highly recommended for accuracy)
    - doi= fields (for output reference)

Output Format:
    CSV file with columns:
    - DOI: Digital Object Identifier
    - Title: Paper title
    - Predicted_Course: Classified CS subject (e.g., "Machine Learning", "Databases")

Common CS Courses Detected:
    - Algorithms and Data Structures
    - Computer Graphics
    - Computer Networks
    - Computer Security/Cybersecurity
    - Databases
    - Distributed Systems
    - Human-Computer Interaction
    - Machine Learning/AI
    - Operating Systems
    - Programming Languages
    - Software Engineering
    - Theory of Computation
    - Web Development

Author: GitHub Copilot
Version: 1.0
"""

import argparse
import re
import csv
import os
import time
import random
from openai import OpenAI

def extract_papers_from_bibtex(bibtex_path):
    """Extract paper information from BibTeX file."""
    papers = []
    current_entry = {}
    in_entry = False
    
    try:
        with open(bibtex_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Split by entry boundaries
        entries = re.split(r'@\w+\s*\{', content)[1:]  # Skip first empty split
        
        for entry in entries:
            paper = {}
            
            # Extract DOI
            doi_match = re.search(r'doi\s*=\s*["{]([^}"]+)["}]', entry, re.IGNORECASE)
            if doi_match:
                doi = doi_match.group(1).strip()
                if doi.startswith('https://doi.org/'):
                    doi = doi[16:]
                paper['doi'] = doi
            
            # Extract title (try title first, then booktitle as fallback)
            title_match = re.search(r'\btitle\s*=\s*["{]([^}"]+)["}]', entry, re.IGNORECASE)
            if title_match:
                title = clean_text(title_match.group(1))
                paper['title'] = title
            else:
                # Try booktitle as fallback
                booktitle_match = re.search(r'\bbooktitle\s*=\s*["{]([^}"]+)["}]', entry, re.IGNORECASE)
                if booktitle_match:
                    title = clean_text(booktitle_match.group(1))
                    paper['title'] = title
            
            # Extract abstract
            abstract_match = re.search(r'\babstract\s*=\s*["{]([^}"]+)["}]', entry, re.IGNORECASE)
            if abstract_match:
                abstract = clean_text(abstract_match.group(1))
                paper['abstract'] = abstract
            
            # Only include papers with at least title and DOI
            if paper.get('title') and paper.get('doi'):
                papers.append(paper)
    
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

def classify_paper(client, paper, model="gpt-3.5-turbo"):
    """Classify a paper using OpenAI API."""
    title = paper.get('title', 'No title')
    abstract = paper.get('abstract', 'No abstract available')
    
    # Create prompt
    prompt = f"""Your task is to try to classify each paper based on its title and abstract. The goal is to find papers that are targetting a specific computer science course (like Databases, or Operating Systems). However, not all papers will fit this neat classification, so you can try to come up with a more appropriate label:

    Title: {title}

    Abstract: {abstract}

    Please respond with just the best prediction of course name (e.g., "Machine Learning", "Databases", "Software Engineering", "Computer Networks", "Operating Systems", "Computer Graphics", "Human-Computer Interaction", "Algorithms and Data Structures", "Introductory Programming", "Object-oriented Programming", "Distributed Systems", "Computer Security", "Theory of Computation", "Web Development", or another specific CS course subject or label if more appropriate).

Course Subject:"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert computer science educator who classifies research papers into appropriate undergraduate/graduate CS course subjects."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        predicted_course = response.choices[0].message.content.strip()
        return predicted_course
        
    except Exception as e:
        print(f"Error classifying paper '{title[:50]}...': {e}")
        return f"Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Classify CS papers into course subjects using OpenAI')
    parser.add_argument('-f', '--file', required=True, help='BibTeX file to analyze')
    parser.add_argument('-o', '--output', required=True, help='Output CSV file')
    parser.add_argument('-m', '--model', default='gpt-4o', 
                       help='OpenAI model to use (default: gpt-4o)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed progress')
    parser.add_argument('--delay', type=float, default=1.0, 
                       help='Delay between API calls in seconds (default: 1.0)')
    parser.add_argument('-n', '--sample-size', type=int, 
                       help='Randomly sample n papers instead of processing all')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducible sampling (default: 42)')
    
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
    
    # Check if input file exists
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        return
    
    print(f"Extracting papers from: {args.file}")
    
    # Extract papers from BibTeX
    papers = extract_papers_from_bibtex(args.file)
    if not papers:
        print("No papers with titles and DOIs found.")
        return
    
    print(f"Found {len(papers)} total papers")
    
    # Handle random sampling if requested
    if args.sample_size:
        if args.sample_size > len(papers):
            print(f"Warning: Sample size ({args.sample_size}) is larger than available papers ({len(papers)})")
            print("Processing all available papers instead.")
        else:
            # Set random seed for reproducibility
            random.seed(args.seed)
            papers = random.sample(papers, args.sample_size)
            print(f"Randomly selected {len(papers)} papers for classification (seed: {args.seed})")
    
    print(f"Processing {len(papers)} papers to classify")
    print(f"Using model: {args.model}")
    
    # Classify papers
    results = []
    for i, paper in enumerate(papers, 1):
        if args.verbose:
            title_preview = paper['title'][:180] + "..." if len(paper['title']) > 60 else paper['title']
            print(f"Processing {i}/{len(papers)}: {title_preview}")
        
        predicted_course = classify_paper(client, paper, args.model)
        
        results.append({
            'DOI': paper['doi'],
            'Title': paper['title'],
            'Predicted_Course': predicted_course
        })
        
        if args.verbose:
            print(f"  → {predicted_course}")
        
        # Rate limiting
        if i < len(papers):  # Don't delay after the last paper
            time.sleep(args.delay)
    
    # Save results to CSV
    try:
        with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['DOI', 'Title', 'Predicted_Course']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                writer.writerow(result)
        
        print(f"\nResults saved to: {args.output}")
        
        # Show summary statistics
        course_counts = {}
        for result in results:
            course = result['Predicted_Course']
            course_counts[course] = course_counts.get(course, 0) + 1
        
        print(f"\nClassification Summary:")
        print("-" * 40)
        for course, count in sorted(course_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(results)) * 100
            print(f"{course}: {count} papers ({percentage:.1f}%)")
        
        # Show sampling info if used
        if args.sample_size:
            print(f"\nSampling Info:")
            print(f"Random seed used: {args.seed}")
            print(f"Sample size: {len(results)} out of total available papers")
        
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    main()