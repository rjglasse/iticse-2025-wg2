"""
Topic Frequency Analyzer for BibTeX Files

This utility analyzes the frequency of specific topics within BibTeX files by searching
through titles, abstracts, keywords, and other content. It's particularly useful for 
academic research analysis, literature reviews, and understanding topic distributions
in bibliographic databases.

Features:
- Extracts and parses BibTeX entries with DOI information
- Searches for user-defined topics within entry content
- Generates frequency statistics and detailed reports
- Creates horizontal bar charts for visual analysis with beautiful viridis color palette
- Exports results to CSV format for further analysis
- Supports case-sensitive and case-insensitive matching

Typical Use Cases:
- Analyzing research trends in academic literature
- Identifying popular topics in conference proceedings
- Literature review preparation and topic clustering
- Research domain analysis and gap identification

Requirements:
- Python 3.6+
- matplotlib (for chart generation): pip install matplotlib

Usage Examples:
    # Basic frequency analysis
    python topic_frequency.py -t topics.txt -b papers.bib

    # Generate a bar chart with top 15 topics
    python topic_frequency.py -t topics.txt -b papers.bib -p --max-topics 15

    # Detailed analysis with CSV export and chart
    python topic_frequency.py -t topics.txt -b papers.bib -v -o results.csv -p

    # Search for a specific topic with detailed paper list
    python topic_frequency.py -t topics.txt -b papers.bib -s "machine learning"

    # Case-sensitive analysis with custom chart filename
    python topic_frequency.py -t topics.txt -b papers.bib -c -p --chart-output analysis.png

Input File Formats:
    Topics file: Plain text file with one topic per line
    BibTeX file: Standard BibTeX format (.bib files)

Output Formats:
    Console: Formatted frequency statistics
    CSV: Topic,Frequency,DOIs,Titles columns
    PNG: Horizontal bar chart visualization

Author: GitHub Copilot
Version: 1.0
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def extract_topics_from_file(topics_file):
    """Extract topics from a file (one topic per line)."""
    topics = []
    try:
        with open(topics_file, 'r', encoding='utf-8') as f:
            for line in f:
                topic = line.strip()
                if topic:
                    topics.append(topic)
    except Exception as e:
        print(f"Error reading topics file {topics_file}: {e}")
        return []
    
    return topics

def extract_entries_from_bibtex(bibtex_path):
    """Extract entries with DOIs from a BibTeX file."""
    entries = []
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
                    current_entry = {'content': line + '\n'}
                    # Extract citation key
                    match = re.search(r'^@\w+\s*\{\s*(\w+)', line)
                    if match:
                        current_key = match.group(1)
                        current_entry['key'] = current_key
                
                # Add content to current entry
                elif in_entry:
                    current_entry['content'] += line + '\n'
                    
                    # Extract DOI if present
                    doi_match = re.search(r'doi\s*=\s*["{]([^}"]+)["}]', line, re.IGNORECASE)
                    if doi_match:
                        doi = doi_match.group(1).strip()
                        if doi.startswith('https://doi.org/'):
                            doi = doi[16:]
                        current_entry['doi'] = doi
                    
                    # Extract title if present
                    title_match = re.search(r'(?<![a-zA-Z])title\s*=\s*["{]([^}"]+)["}]', line, re.IGNORECASE)
                    if title_match:
                        title = title_match.group(1).strip()
                        current_entry['title'] = title
                    
                    # Check for entry end
                    if line == '}':
                        in_entry = False
                        if 'doi' in current_entry:  # Only keep entries with DOIs
                            entries.append(current_entry)
                        current_entry = {}
                        current_key = None
    
    except Exception as e:
        print(f"Error reading BibTeX file {bibtex_path}: {e}")
    
    return entries

def analyze_topic_frequency(entries, topics, case_sensitive=False):
    """Analyze frequency of topics in BibTeX entries."""
    topic_frequency = defaultdict(int)
    topic_entries = defaultdict(list)
    
    for entry in entries:
        content = entry.get('content', '').lower() if not case_sensitive else entry.get('content', '')
        
        for topic in topics:
            topic_to_search = topic if case_sensitive else topic.lower()
            if topic_to_search in content:
                topic_frequency[topic] += 1
                topic_entries[topic].append(entry)
    
    return topic_frequency, topic_entries

def create_bar_chart(sorted_topics, output_file='topic_frequency_chart.png', max_topics=20):
    """Create a horizontal bar chart of topic frequencies and save as PNG."""
    try:
        # Limit the number of topics to display for readability
        display_topics = sorted_topics[:max_topics]
        
        if not display_topics:
            print("No topics to plot.")
            return False
        
        # Extract topics and frequencies
        topics = [item[0] for item in display_topics]
        frequencies = [item[1] for item in display_topics]
        
        # Create figure with vertical layout for horizontal bars
        plt.figure(figsize=(12, max(8, len(topics) * 0.4)))
        
        # Create beautiful fading color palette (viridis gradient from dark to light)
        num_bars = len(topics)
        colors = plt.cm.viridis(np.linspace(0.85, 0.15, num_bars))  # Deep purple to bright teal
        
        # Create horizontal bar chart with gradient colors
        bars = plt.barh(topics, frequencies, color=colors, alpha=0.9, 
                       edgecolor='white', linewidth=0.8)
        
        # Customize the chart
        plt.title('Topic Frequency Analysis', fontsize=18, fontweight='bold', pad=25, color='#2c3e50')
        plt.xlabel('Frequency', fontsize=14, fontweight='bold', color='#34495e')
        plt.ylabel('Topics', fontsize=14, fontweight='bold', color='#34495e')
        
        # Invert y-axis so highest frequency is on top
        plt.gca().invert_yaxis()
        
        # Add value labels at the end of bars
        max_freq = max(frequencies)
        for bar, freq in zip(bars, frequencies):
            plt.text(bar.get_width() + max_freq * 0.01, bar.get_y() + bar.get_height()/2,
                    str(freq), ha='left', va='center', fontweight='bold', fontsize=11, color='#2c3e50')
        
        # Add grid for better readability
        plt.grid(axis='x', alpha=0.3, linestyle='--', color='#bdc3c7')
        
        # Style the axes
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#95a5a6')
        ax.spines['bottom'].set_color('#95a5a6')
        ax.tick_params(colors='#34495e', labelsize=11)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Save the chart
        plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()  # Close the figure to free memory
        
        print(f"Bar chart saved to: {output_file}")
        return True
        
    except ImportError:
        print("Error: matplotlib is required for plotting. Install with: pip install matplotlib")
        return False
    except Exception as e:
        print(f"Error creating bar chart: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Analyze topic frequency in BibTeX entries')
    parser.add_argument('-t', '--topics', required=True, help='File containing topics (one per line)')
    parser.add_argument('-b', '--bibtex', required=True, help='BibTeX file to analyze')
    parser.add_argument('-o', '--output', help='Output file for results')
    parser.add_argument('-c', '--case-sensitive', action='store_true', help='Use case-sensitive matching')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output with DOIs')
    parser.add_argument('-s', '--specific-topic', help='Show papers for a specific topic')
    parser.add_argument('-p', '--plot-chart', action='store_true', help='Export bar chart to PNG')
    parser.add_argument('--chart-output', help='Output file for chart (default: topic_frequency_chart.png)', 
                       default='topic_frequency_chart.png')
    parser.add_argument('--max-topics', type=int, default=20, 
                       help='Maximum number of topics to display in chart (default: 20)')
    args = parser.parse_args()
    
    # Load topics
    topics = extract_topics_from_file(args.topics)
    if not topics:
        print("No topics found in the topics file.")
        return
    
    # Add specific topic if provided
    if args.specific_topic and args.specific_topic not in topics:
        topics.append(args.specific_topic)
    
    print(f"Loaded {len(topics)} topics for analysis")
    
    # Parse BibTeX file
    entries = extract_entries_from_bibtex(args.bibtex)
    if not entries:
        print(f"No entries with DOIs found in {args.bibtex}")
        return
    
    print(f"Found {len(entries)} BibTeX entries with DOIs")
    
    # Analyze topic frequency
    topic_frequency, topic_entries = analyze_topic_frequency(entries, topics, args.case_sensitive)
    
    # If specific topic is provided, show papers for that topic
    if args.specific_topic:
        specific_topic = args.specific_topic
        if specific_topic in topic_frequency:
            print(f"\nPapers containing topic '{specific_topic}' ({topic_frequency[specific_topic]} occurrences):")
            print("-" * (40 + len(specific_topic)))
            for i, entry in enumerate(topic_entries[specific_topic], 1):
                title = entry.get('title', 'No title available')
                doi = entry.get('doi', 'No DOI available')
                print(f"{i}. {title}")
                print(f"   DOI: {doi}")
                print()
        else:
            print(f"\nNo papers found containing topic '{specific_topic}'")
        
        # If specific topic only requested, exit
        if not args.verbose and not args.output and not args.plot_chart:
            return
    
    # Sort topics by frequency (descending)
    sorted_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)
    
    # Filter out topics with 0 frequency for plotting
    sorted_topics = [(topic, freq) for topic, freq in sorted_topics if freq > 0]
    
    # Print results for all topics
    if args.verbose or not args.specific_topic:
        print("\nTopic Frequency Analysis:")
        print("------------------------")
        
        if not sorted_topics:
            print("No topics found in the BibTeX entries.")
            return
        
        for topic, count in sorted_topics:
            print(f"{topic}: {count} occurrences")
            if args.verbose:
                print("  DOIs:")
                for entry in topic_entries[topic]:
                    doi = entry.get('doi', 'No DOI available')
                    print(f"    - {doi}")
    
    # Create bar chart if requested
    if args.plot_chart:
        create_bar_chart(sorted_topics, args.chart_output, args.max_topics)
    
    # Write results to file if requested
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write("Topic,Frequency,DOIs,Titles\n")
                for topic, count in sorted_topics:
                    doi_list = "|".join([entry.get('doi', 'No DOI') for entry in topic_entries[topic]])
                    title_list = "|".join([entry.get('title', 'No Title') for entry in topic_entries[topic]])
                    f.write(f'"{topic}",{count},"{doi_list}","{title_list}"\n')
            print(f"\nResults saved to: {args.output}")
        except Exception as e:
            print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    main()