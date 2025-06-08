"""
TF-IDF Analysis Tool for BibTeX Files

This utility performs Term Frequency-Inverse Document Frequency (TF-IDF) analysis on 
academic papers stored in BibTeX format. TF-IDF is a numerical statistic that reflects 
how important a word is to a document in a collection of documents, making it ideal 
for identifying key terms and themes in academic literature.

What is TF-IDF?
TF-IDF combines two metrics:
- Term Frequency (TF): How often a term appears in a document
- Inverse Document Frequency (IDF): How rare or common a term is across all documents
The product gives higher scores to terms that are frequent in specific documents but 
rare across the entire collection, highlighting distinctive vocabulary.

Features:
- Extracts text from BibTeX titles, abstracts, and keywords
- Removes LaTeX commands and normalizes text
- Filters stopwords and applies document frequency thresholds
- Calculates TF-IDF scores for comprehensive term analysis
- Identifies globally important terms across the corpus
- Generates detailed per-document term rankings
- Exports comprehensive results to text files

Use Cases:
- Literature review preparation and topic identification
- Research trend analysis in academic fields
- Keyword extraction for paper categorization
- Content similarity analysis between papers
- Academic corpus exploration and theme discovery
- Identifying distinctive terminology in research domains

Requirements:
- Python 3.6+
- BibTeX files with title, abstract, or keyword fields

Usage Examples:
    # Basic TF-IDF analysis
    python tf-idf.py -f papers.bib

    # Custom filtering and output
    python tf-idf.py -f papers.bib --min-df 3 --max-df 0.7 -o analysis.txt

    # Detailed verbose output
    python tf-idf.py -f papers.bib -v --top-n 15

    # Analyze specific academic corpus
    python tf-idf.py -f bibfiles/acm_chatgpt.bib -o chatgpt_tfidf.txt

Input Requirements:
    BibTeX file: Standard .bib format with entries containing:
    - title= fields (required for meaningful analysis)
    - abstract= fields (highly recommended)
    - keywords= fields (optional but valuable)
    - doi= fields (for reference tracking)

Output:
    Console: Top global terms and statistics
    Text file: Comprehensive analysis with per-document breakdowns
    
Parameters:
    --min-df: Minimum documents a term must appear in (default: 2)
    --max-df: Maximum ratio of documents a term can appear in (default: 0.8)
    --top-n: Number of top terms to show per document (default: 10)

Algorithm Details:
    1. Text extraction and cleaning (LaTeX removal, normalization)
    2. Tokenization and stopword filtering
    3. Vocabulary building with frequency thresholds
    4. TF calculation: term_freq / total_words_in_doc
    5. IDF calculation: log(total_docs / docs_containing_term)
    6. TF-IDF scoring: TF * IDF for each term-document pair

Author: GitHub Copilot
Version: 1.2
"""

import argparse
import re
import os
from collections import defaultdict, Counter
import math
from pathlib import Path
import string

def extract_text_from_bibtex(bibtex_path):
    """Extract text content from BibTeX entries."""
    documents = []
    current_entry = {}
    current_key = None
    in_entry = False
    
    try:
        with open(bibtex_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                
                # Check for entry start
                if re.match(r'^@\w+\s*\{', line):
                    in_entry = True
                    current_entry = {'content': ''}
                    # Extract citation key
                    match = re.search(r'^@\w+\s*\{\s*([^,]+)', line)
                    if match:
                        current_key = match.group(1).strip()
                        current_entry['key'] = current_key
                
                # Process content within entry
                elif in_entry:
                    # Extract title
                    title_match = re.search(r'title\s*=\s*["{]([^}"]+)["}]', line, re.IGNORECASE)
                    if title_match:
                        current_entry['title'] = clean_text(title_match.group(1))
                    
                    # Extract abstract
                    abstract_match = re.search(r'abstract\s*=\s*["{]([^}"]+)["}]', line, re.IGNORECASE)
                    if abstract_match:
                        current_entry['abstract'] = clean_text(abstract_match.group(1))
                    
                    # Extract keywords
                    keywords_match = re.search(r'keywords\s*=\s*["{]([^}"]+)["}]', line, re.IGNORECASE)
                    if keywords_match:
                        current_entry['keywords'] = clean_text(keywords_match.group(1))
                    
                    # Extract DOI
                    doi_match = re.search(r'doi\s*=\s*["{]([^}"]+)["}]', line, re.IGNORECASE)
                    if doi_match:
                        doi = doi_match.group(1).strip()
                        if doi.startswith('https://doi.org/'):
                            doi = doi[16:]
                        current_entry['doi'] = doi
                    
                    # Check for entry end
                    if line == '}':
                        in_entry = False
                        if current_entry.get('title') or current_entry.get('abstract'):
                            # Combine all text content
                            text_parts = []
                            if current_entry.get('title'):
                                text_parts.append(current_entry['title'])
                            if current_entry.get('abstract'):
                                text_parts.append(current_entry['abstract'])
                            if current_entry.get('keywords'):
                                text_parts.append(current_entry['keywords'])
                            
                            current_entry['content'] = ' '.join(text_parts)
                            documents.append(current_entry)
                        current_entry = {}
                        current_key = None
    
    except Exception as e:
        print(f"Error reading BibTeX file {bibtex_path}: {e}")
    
    return documents

def clean_text(text):
    """Clean and normalize text for TF-IDF analysis."""
    # Remove LaTeX commands and special characters
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # Remove punctuation and convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.lower()
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text

def tokenize(text):
    """Tokenize text into words."""
    # Split on whitespace and filter out empty strings and very short words
    words = [word for word in text.split() if len(word) > 2]
    return words

def create_stopwords():
    """Create a set of common stopwords."""
    return {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
        'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
        'very', 'can', 'will', 'just', 'should', 'now', 'also', 'this', 'that', 'these',
        'those', 'are', 'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
        'did', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'will'
    }

def calculate_tf(doc_words):
    """Calculate term frequency for a document."""
    tf = defaultdict(float)
    total_words = len(doc_words)
    
    for word in doc_words:
        tf[word] += 1.0 / total_words
    
    return dict(tf)

def calculate_idf(documents, vocabulary):
    """Calculate inverse document frequency for all terms."""
    idf = {}
    total_docs = len(documents)
    
    for term in vocabulary:
        docs_containing_term = sum(1 for doc in documents if term in doc)
        idf[term] = math.log(total_docs / docs_containing_term)
    
    return idf

def calculate_tfidf(documents, min_df=2, max_df_ratio=0.8):
    """Calculate TF-IDF scores for all documents."""
    stopwords = create_stopwords()
    
    # Tokenize all documents
    tokenized_docs = []
    for doc in documents:
        words = tokenize(doc['content'])
        words = [word for word in words if word not in stopwords]
        tokenized_docs.append(words)
    
    # Build vocabulary with document frequency filtering
    word_doc_count = defaultdict(int)
    for doc_words in tokenized_docs:
        unique_words = set(doc_words)
        for word in unique_words:
            word_doc_count[word] += 1
    
    # Filter vocabulary
    total_docs = len(documents)
    max_df = int(max_df_ratio * total_docs)
    vocabulary = {word for word, count in word_doc_count.items() 
                  if min_df <= count <= max_df}
    
    print(f"Vocabulary size after filtering: {len(vocabulary)} terms")
    print(f"Min document frequency: {min_df}")
    print(f"Max document frequency: {max_df}")
    
    # Calculate IDF
    idf = calculate_idf(tokenized_docs, vocabulary)
    
    # Calculate TF-IDF for each document
    tfidf_docs = []
    for i, doc_words in enumerate(tokenized_docs):
        tf = calculate_tf(doc_words)
        tfidf = {}
        
        for term in vocabulary:
            if term in tf:
                tfidf[term] = tf[term] * idf[term]
            else:
                tfidf[term] = 0.0
        
        tfidf_docs.append({
            'tfidf': tfidf,
            'metadata': documents[i]
        })
    
    return tfidf_docs, vocabulary, idf

def get_top_terms(tfidf_doc, n=10):
    """Get top N terms by TF-IDF score for a document."""
    sorted_terms = sorted(tfidf_doc['tfidf'].items(), key=lambda x: x[1], reverse=True)
    return sorted_terms[:n]

def get_top_terms_global(tfidf_docs, vocabulary, n=50):
    """Get top N terms globally across all documents."""
    global_scores = defaultdict(float)
    
    for doc in tfidf_docs:
        for term, score in doc['tfidf'].items():
            global_scores[term] += score
    
    sorted_terms = sorted(global_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_terms[:n]

def save_results(tfidf_docs, vocabulary, output_file, top_n=10):
    """Save TF-IDF results to a file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("TF-IDF Analysis Results\n")
        f.write("="*50 + "\n\n")
        
        # Global top terms
        global_top = get_top_terms_global(tfidf_docs, vocabulary, 20)
        f.write("Top 20 Terms Globally:\n")
        f.write("-" * 30 + "\n")
        for term, score in global_top:
            f.write(f"{term}: {score:.4f}\n")
        f.write("\n")
        
        # Per-document analysis
        f.write("Per-Document Analysis:\n")
        f.write("-" * 30 + "\n")
        for i, doc in enumerate(tfidf_docs):
            f.write(f"\nDocument {i+1}:\n")
            if doc['metadata'].get('title'):
                f.write(f"Title: {doc['metadata']['title'][:100]}...\n")
            if doc['metadata'].get('doi'):
                f.write(f"DOI: {doc['metadata']['doi']}\n")
            
            top_terms = get_top_terms(doc, top_n)
            f.write(f"Top {top_n} terms:\n")
            for term, score in top_terms:
                f.write(f"  {term}: {score:.4f}\n")
            f.write("\n")

def main():
    parser = argparse.ArgumentParser(description='Perform TF-IDF analysis on BibTeX files')
    parser.add_argument('-f', '--file', required=True, help='BibTeX file to analyze')
    parser.add_argument('-o', '--output', help='Output file for results', default='tfidf_results.txt')
    parser.add_argument('--min-df', type=int, default=2, 
                        help='Minimum document frequency for terms (default: 2)')
    parser.add_argument('--max-df', type=float, default=0.8, 
                        help='Maximum document frequency ratio (default: 0.8)')
    parser.add_argument('--top-n', type=int, default=10, 
                        help='Number of top terms to show per document (default: 10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"Error: File '{args.file}' not found.")
        return
    
    print(f"Analyzing BibTeX file: {args.file}")
    
    # Extract documents
    documents = extract_text_from_bibtex(args.file)
    if not documents:
        print("No documents with text content found.")
        return
    
    print(f"Found {len(documents)} documents with text content")
    
    # Calculate TF-IDF
    print("Calculating TF-IDF scores...")
    tfidf_docs, vocabulary, idf = calculate_tfidf(documents, args.min_df, args.max_df)
    
    # Display results
    if args.verbose:
        print(f"\nTop {min(10, len(documents))} documents by top term scores:")
        for i, doc in enumerate(tfidf_docs[:10]):
            print(f"\nDocument {i+1}:")
            if doc['metadata'].get('title'):
                print(f"  Title: {doc['metadata']['title'][:80]}...")
            top_terms = get_top_terms(doc, 5)
            print(f"  Top terms: {', '.join([f'{term}({score:.3f})' for term, score in top_terms])}")
    
    # Show global top terms
    global_top = get_top_terms_global(tfidf_docs, vocabulary, 50)
    print(f"\nTop 20 terms globally:")
    for i, (term, score) in enumerate(global_top, 1):
        print(f"{i:2d}. {term}: {score:.4f}")
    
    # Save results
    save_results(tfidf_docs, vocabulary, args.output, args.top_n)
    print(f"\nDetailed results saved to: {args.output}")

if __name__ == "__main__":
    main()