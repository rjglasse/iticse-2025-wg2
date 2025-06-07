import argparse
import re
from collections import defaultdict
from pathlib import Path

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

def main():
    parser = argparse.ArgumentParser(description='Analyze topic frequency in BibTeX entries')
    parser.add_argument('-t', '--topics', required=True, help='File containing topics (one per line)')
    parser.add_argument('-b', '--bibtex', required=True, help='BibTeX file to analyze')
    parser.add_argument('-o', '--output', help='Output file for results')
    parser.add_argument('-c', '--case-sensitive', action='store_true', help='Use case-sensitive matching')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output with DOIs')
    parser.add_argument('-s', '--specific-topic', help='Show papers for a specific topic')
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
        if not args.verbose and not args.output:
            return
    
    # Sort topics by frequency (descending)
    sorted_topics = sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)
    
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