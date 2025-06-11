#!/usr/bin/env python3
"""
Springer RSS Feed Crawler for Academic Papers

This utility crawls Springer RSS feeds to extract bibliographic information from
academic papers matching specific search criteria. It's designed to work with
Springer's RSS search interface and can handle pagination across multiple pages
of results.

Features:
- Crawls multiple pages of Springer RSS feeds automatically
- Extracts titles, authors, DOIs, abstracts, and publication details
- Handles pagination with configurable delays between requests
- Exports results to BibTeX and CSV formats
- Provides progress tracking and error handling
- Respects rate limits to avoid overwhelming the server
- Supports custom date ranges and search parameters

Use Cases:
- Systematic literature reviews requiring Springer content
- Building bibliographic databases from Springer publications
- Academic research data collection and analysis
- Creating reference lists for specific research domains
- Automated literature discovery and cataloging

Requirements:
- Python 3.6+
- requests library: pip install requests
- xml.etree.ElementTree (built-in)
- urllib.parse (built-in)

Usage Examples:
    # Crawl first 10 pages with default settings
    python springer_crawl.py -u "base_url" --max-pages 10

    # Crawl with custom output and delay
    python springer_crawl.py -u "base_url" -o springer_results --delay 2.0 --max-pages 20

    # Verbose crawling with detailed progress
    python springer_crawl.py -u "base_url" -v --max-pages 5 -o detailed_results

Input Requirements:
    Base RSS URL from Springer search interface
    URL should contain search parameters, date ranges, and filters

Output Formats:
    BibTeX (.bib): Standard bibliographic format
    CSV (.csv): Tabular format with all extracted fields
    Summary (.txt): Statistics and processing information

Error Handling:
    - Network timeout and connection issues
    - Malformed XML responses
    - Missing bibliographic fields
    - Rate limiting and server errors

Author: GitHub Copilot
Version: 1.0
"""

import argparse
import csv
import re
import sys
import time
import urllib.parse
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    import requests
except ImportError:
    print("Error: requests library is required. Install with: pip install requests")
    sys.exit(1)

class SpringerCrawler:
    def __init__(self, base_url, delay=1.5, verbose=False):
        """
        Initialize the Springer RSS crawler.
        
        Args:
            base_url (str): Base RSS URL from Springer search
            delay (float): Delay between requests in seconds
            verbose (bool): Enable verbose output
        """
        self.base_url = base_url
        self.delay = delay
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.papers = []
        self.total_papers = 0
        
    def log(self, message):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def clean_text(self, text):
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Handle HTML entities first
        import html
        text = html.unescape(text)
        
        # Remove HTML tags more robustly
        # This handles nested tags and malformed HTML better
        text = re.sub(r'<[^>]*>', '', text)
        
        # Handle common HTML entities that might remain
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&apos;', "'")
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove or escape problematic characters for BibTeX
        text = text.replace('{', '').replace('}', '')
        text = text.replace('"', "'")
        
        return text.strip()
     
    def extract_doi_from_guid(self, guid):
        """Extract DOI from GUID field."""
        if not guid:
            return None
        
        # Check if GUID is already a DOI (common pattern)
        doi_patterns = [
            r'10\.1007/[^?&\s]+',           # Standard Springer DOI
            r'10\.1140/[^?&\s]+',           # EPJ Data Science DOIs
            r'10\.1186/[^?&\s]+',           # BioMed Central DOIs  
            r'10\.1038/[^?&\s]+',           # Nature DOIs
            r'10\.1017/[^?&\s]+',           # Cambridge DOIs
            r'10\.\d{4,}/[^?&\s]+',         # Generic DOI pattern
        ]
        
        for pattern in doi_patterns:
            match = re.search(pattern, guid)
            if match:
                return match.group(0)
        
        return None
    
    def parse_rss_feed(self, url, page_num=1):
        """
        Parse a single RSS feed page and extract paper information.
        
        Args:
            url (str): RSS feed URL
            page_num (int): Page number for logging
            
        Returns:
            list: List of paper dictionaries
        """
        papers = []
        
        try:
            self.log(f"Fetching page {page_num}: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Check if we got HTML instead of RSS (authentication redirect)
            content_type = response.headers.get('content-type', '').lower()
            if 'html' in content_type:
                print(f"Warning: Page {page_num} returned HTML instead of RSS XML.")
                print("This usually means authentication is required or the URL is incorrect.")
                print(f"Content preview: {response.text[:200]}...")
                return []
            
            # Parse XML
            try:
                root = ET.fromstring(response.content)
            except ET.ParseError as parse_error:
                print(f"XML Parse Error on page {page_num}: {parse_error}")
                print(f"Response content type: {content_type}")
                print(f"Response preview: {response.text[:500]}...")
                return []
            
            # Find all items (papers)
            items = root.findall('.//item')
            self.log(f"Found {len(items)} papers on page {page_num}")
            
            if len(items) == 0:
                # Check if this is a valid RSS feed with no items
                channel = root.find('.//channel')
                if channel is not None:
                    title = channel.find('title')
                    if title is not None:
                        print(f"Valid RSS feed found but no items on page {page_num}. Feed title: {title.text}")
                    else:
                        print(f"Valid RSS feed found but no items on page {page_num}")
                else:
                    print(f"Invalid RSS structure on page {page_num}")
                return []
            
            for i, item in enumerate(items, 1):
                try:
                    paper = self.extract_paper_info(item)
                    if paper:
                        papers.append(paper)
                        self.log(f"  Paper {i}: {paper.get('title', 'No title')[:60]}...")
                    else:
                        # Log when a paper is skipped
                        title_elem = item.find('title')
                        title_text = title_elem.text if title_elem is not None and title_elem.text else "Unknown"
                        self.log(f"  Paper {i}: SKIPPED - {title_text[:60]}... (missing required fields)")
                except Exception as e:
                    # Log when individual paper processing fails with more details
                    title_elem = item.find('title')
                    title_text = title_elem.text if title_elem is not None and title_elem.text else "Unknown"
                    print(f"  Error processing paper {i} '{title_text[:60]}...': {e}")
                    
                    # Add more detailed debugging information
                    if self.verbose:
                        print(f"    Exception type: {type(e).__name__}")
                        print(f"    Full error: {str(e)}")
                        
                        # Try to extract basic info for debugging
                        try:
                            link_elem = item.find('link')
                            guid_elem = item.find('guid')
                            pubdate_elem = item.find('pubDate')
                            
                            print(f"    Link exists: {link_elem is not None}")
                            print(f"    Link text: {link_elem.text if link_elem is not None else 'None'}")
                            print(f"    GUID exists: {guid_elem is not None}")
                            print(f"    GUID text: {guid_elem.text if guid_elem is not None else 'None'}")
                            print(f"    PubDate exists: {pubdate_elem is not None}")
                            print(f"    PubDate text: {pubdate_elem.text if pubdate_elem is not None else 'None'}")
                        except Exception as debug_e:
                            print(f"    Additional debugging failed: {debug_e}")
                    
                    continue
                
        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
        except Exception as e:
            print(f"Unexpected error processing page {page_num}: {e}")
        
        return papers
    
    def extract_paper_info(self, item):
        """
        Extract bibliographic information from an RSS item.
        
        Args:
            item: XML element representing a paper
            
        Returns:
            dict: Paper information dictionary
        """
        paper = {}
        
        # Extract title using robust method that handles HTML content
        title_elem = item.find('title')
        if title_elem is not None:
            # Use itertext() to get all text content, including from child elements
            try:
                all_text = ''.join(title_elem.itertext())
                if all_text and all_text.strip():
                    # Clean the extracted title text
                    clean_title = self.clean_text(all_text)
                    if clean_title:
                        paper['title'] = clean_title
                elif title_elem.text and title_elem.text.strip():
                    # Fallback to direct text if itertext is empty
                    clean_title = self.clean_text(title_elem.text)
                    if clean_title:
                        paper['title'] = clean_title
            except Exception as e:
                # Final fallback to direct text access
                if title_elem.text and title_elem.text.strip():
                    clean_title = self.clean_text(title_elem.text)
                    if clean_title:
                        paper['title'] = clean_title
                        if self.verbose:
                            print(f"Warning: itertext() failed, used direct text: {e}")
        
        # Extract GUID as identifier and additional DOI source
        guid_elem = item.find('guid')
        if guid_elem is not None and guid_elem.text:
            paper['doi'] = guid_elem.text.strip()
         
        # Extract publication date
        pubdate_elem = item.find('pubDate')
        if pubdate_elem is not None and pubdate_elem.text:
            paper['pub_date'] = pubdate_elem.text.strip()
            # Try to extract year safely
            try:
                year_match = re.search(r'\b(20\d{2})\b', pubdate_elem.text)
                if year_match:
                    paper['year'] = year_match.group(1)
            except (AttributeError, TypeError) as e:
                if self.verbose:
                    print(f"    Warning: Could not extract year from date '{pubdate_elem.text}': {e}")
        
        # Only return papers with at least title and doi
        if paper.get('title') and paper.get('doi'):
            return paper
        
        # Log what's missing for debugging
        missing = []
        if not paper.get('title'):
            missing.append('title')
        if not paper.get('doi'):
            missing.append('doi')
        
        # This will trigger the "SKIPPED" message in the calling function
        return None
    
    def build_page_url(self, page_num):
        """
        Build URL for a specific page number.
        
        Args:
            page_num (int): Page number (1-based)
            
        Returns:
            str: Complete URL for the page
        """
        # Parse the base URL
        parsed = urllib.parse.urlparse(self.base_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        
        # Determine pagination method based on URL structure
        if 'new-search=true' in self.base_url:
            # For new-search URLs, use page parameter (page=1, page=2, etc.)
            query_params.pop('start', None)  # Remove start if present
            if page_num > 1:
                query_params['page'] = [str(page_num)]
            else:
                query_params.pop('page', None)  # Remove page param for first page
        else:
            # For regular RSS feeds, use start offset parameter
            start_offset = (page_num - 1) * 20
            query_params.pop('page', None)  # Remove page if present
            if page_num > 1:
                query_params['start'] = [str(start_offset)]
            else:
                query_params.pop('start', None)  # Remove start param for first page
        
        # Remove other pagination parameters
        query_params.pop('p', None)
        
        # Rebuild the URL
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        new_url = urllib.parse.urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))
        
        return new_url
    
    def crawl_pages(self, max_pages=42):
        """
        Crawl multiple pages of results.
        
        Args:
            max_pages (int): Maximum number of pages to crawl
            
        Returns:
            list: All papers found across all pages
        """
        all_papers = []
        start_time = time.time()
        
        print(f"Starting crawl of up to {max_pages} pages...")
        print(f"Base URL: {self.base_url}")
        print(f"Delay between requests: {self.delay} seconds")
        print()
        
        for page_num in range(1, max_pages + 1):
            # Build URL for this page
            page_url = self.build_page_url(page_num)
            
            # Fetch and parse this page
            page_papers = self.parse_rss_feed(page_url, page_num)
            
            if not page_papers:
                print(f"No papers found on page {page_num}. Stopping crawl.")
                break
            
            all_papers.extend(page_papers)
            
            # Progress update
            elapsed = time.time() - start_time
            avg_time_per_page = elapsed / page_num
            estimated_remaining = (max_pages - page_num) * avg_time_per_page
            eta_minutes = int(estimated_remaining // 60)
            eta_seconds = int(estimated_remaining % 60)
            
            print(f"Page {page_num}/{max_pages} complete. "
                  f"Found {len(page_papers)} papers. "
                  f"Total: {len(all_papers)} papers. "
                  f"ETA: {eta_minutes}m {eta_seconds}s")
            
            # Rate limiting delay
            if page_num < max_pages:
                time.sleep(self.delay)
        
        self.papers = all_papers
        self.total_papers = len(all_papers)
        
        total_time = time.time() - start_time
        print(f"\nCrawl completed in {total_time:.1f} seconds")
        print(f"Total papers collected: {self.total_papers}")
        
        return all_papers
    
    def export_to_bibtex(self, output_file):
        """Export papers to BibTeX format."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, paper in enumerate(self.papers, 1):
                    # Generate BibTeX key
                    title_words = paper.get('title', '').split()[:3]
                    year = paper.get('year', '2024')
                    key = f"springer{year}_{i:03d}"
                    
                    # Write BibTeX entry
                    f.write(f"@article{{{key},\n")
                    
                    if paper.get('title'):
                        f.write(f"  title={{{paper['title']}}},\n")
                    
                    if paper.get('author_string'):
                        f.write(f"  author={{{paper['author_string']}}},\n")
                    
                    if paper.get('year'):
                        f.write(f"  year={{{paper['year']}}},\n")
                    
                    if paper.get('doi'):
                        f.write(f"  doi={{{paper['doi']}}},\n")
                    
                    if paper.get('url'):
                        f.write(f"  url={{{paper['url']}}},\n")
                    
                    if paper.get('abstract'):
                        f.write(f"  abstract={{{paper['abstract']}}},\n")
                    
                    f.write(f"  publisher={{Springer}},\n")
                    f.write(f"  note={{Crawled from Springer RSS feed}}\n")
                    f.write("}\n\n")
            
            print(f"BibTeX export saved to: {output_file}")
            
        except Exception as e:
            print(f"Error exporting to BibTeX: {e}")
    
    def export_to_csv(self, output_file):
        """Export papers to CSV format."""
        try:
            fieldnames = ['doi', 'title', 'year']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for paper in self.papers:
                    # Convert authors list to string
                    writer.writerow({k: paper.get(k, '') for k in fieldnames})
            
            print(f"CSV export saved to: {output_file}")
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
    
    def print_summary(self):
        """Print summary statistics."""
        if not self.papers:
            print("No papers found.")
            return
        
        print(f"\nCrawl Summary:")
        print(f"==============")
        print(f"Total papers: {len(self.papers)}")
        
        # Count papers with DOIs
        papers_with_dois = sum(1 for p in self.papers if p.get('doi'))
        print(f"Papers with DOIs: {papers_with_dois} ({papers_with_dois/len(self.papers)*100:.1f}%)")
        
        # Count papers with abstracts
        papers_with_abstracts = sum(1 for p in self.papers if p.get('abstract'))
        print(f"Papers with abstracts: {papers_with_abstracts} ({papers_with_abstracts/len(self.papers)*100:.1f}%)")
        
        # Count papers with authors
        papers_with_authors = sum(1 for p in self.papers if p.get('authors'))
        print(f"Papers with authors: {papers_with_authors} ({papers_with_authors/len(self.papers)*100:.1f}%)")
        
        # Show year distribution
        years = {}
        for paper in self.papers:
            year = paper.get('year', 'Unknown')
            years[year] = years.get(year, 0) + 1
        
        print(f"\nYear distribution:")
        for year in sorted(years.keys()):
            print(f"  {year}: {years[year]} papers")
        
        # Show sample papers
        print(f"\nSample papers (first 3):")
        for i, paper in enumerate(self.papers[:3], 1):
            print(f"  {i}. {paper.get('title', 'No title')}")
            if paper.get('doi'):
                print(f"     DOI: {paper['doi']}")
            print()

def main():
    parser = argparse.ArgumentParser(description='Crawl Springer RSS feeds for academic papers')
    parser.add_argument('-u', '--url', required=True, 
                       help='Base RSS URL from Springer search')
    parser.add_argument('-o', '--output', default='springer_results',
                       help='Output file prefix (default: springer_results)')
    parser.add_argument('--max-pages', type=int, default=42,
                       help='Maximum number of pages to crawl (default: 42)')
    parser.add_argument('--delay', type=float, default=1.5,
                       help='Delay between requests in seconds (default: 1.5)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--bibtex-only', action='store_true',
                       help='Only export BibTeX format (skip CSV)')
    parser.add_argument('--csv-only', action='store_true',
                       help='Only export CSV format (skip BibTeX)')
    parser.add_argument('--convert-kth-url', action='store_true',
                       help='Convert KTH proxy URL to direct Springer URL')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.bibtex_only and args.csv_only:
        print("Error: Cannot specify both --bibtex-only and --csv-only")
        sys.exit(1)
    
    # Handle KTH URL conversion
    url = args.url
    if 'focus.lib.kth.se' in url or args.convert_kth_url:
        print("🔄 Converting KTH proxy URL to direct Springer URL...")
        # Extract the actual Springer URL from the KTH proxy URL
        if 'qurl=' in url:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed.query)
            if 'qurl' in query_params:
                direct_url = urllib.parse.unquote(query_params['qurl'][0])
                print(f"📋 Direct Springer URL: {direct_url}")
                url = direct_url
        else:
            # Convert focus.lib.kth.se domain to link.springer.com
            url = url.replace('link-springer-com.focus.lib.kth.se', 'link.springer.com')
            print(f"📋 Converted URL: {url}")
    
    # Initialize crawler
    crawler = SpringerCrawler(url, delay=args.delay, verbose=args.verbose)
    
    # Crawl pages
    papers = crawler.crawl_pages(max_pages=args.max_pages)
    
    if not papers:
        print("No papers found. Exiting.")
        sys.exit(1)
    
    # Print summary
    crawler.print_summary()
    
    # Export results
    if not args.csv_only:
        bibtex_file = f"{args.output}.bib"
        crawler.export_to_bibtex(bibtex_file)
    
    if not args.bibtex_only:
        csv_file = f"{args.output}.csv"
        crawler.export_to_csv(csv_file)
    
    print(f"\n✅ Springer crawl completed successfully!")
    print(f"📊 Collected {len(papers)} papers from {args.max_pages} pages")

if __name__ == "__main__":
    main()