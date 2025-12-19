#!/usr/bin/env python3
"""
Fetch publications from ORCID API and generate Jekyll markdown files.
Credentials are stored securely in environment variables (GitHub Secrets).
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
import re

# Configuration
ORCID_ID = os.environ.get('ORCID_ID', '')  # Set in GitHub Secrets
CLIENT_ID = os.environ.get('ORCID_CLIENT_ID', '')  # Set in GitHub Secrets
CLIENT_SECRET = os.environ.get('ORCID_CLIENT_SECRET', '')  # Set in GitHub Secrets

# API endpoints
ORCID_TOKEN_URL = 'https://orcid.org/oauth/token'
ORCID_API_BASE = 'https://pub.orcid.org/v3.0'

# Publication categories mapping
CATEGORY_MAPPING = {
    'journal-article': {'category': 'manuscripts', 'display': 'Published Articles'},
    'working-paper': {'category': 'working-papers', 'display': 'Working Papers'},
    'preprint': {'category': 'working-papers', 'display': 'Working Papers'},
    'conference-paper': {'category': 'manuscripts', 'display': 'Published Articles'},
    'book-chapter': {'category': 'manuscripts', 'display': 'Published Articles'},
    'book': {'category': 'manuscripts', 'display': 'Published Articles'},
    'dissertation': {'category': 'manuscripts', 'display': 'Published Articles'},
    'report': {'category': 'working-papers', 'display': 'Working Papers'},
}


def get_access_token():
    """Obtain access token from ORCID API."""
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERROR: ORCID_CLIENT_ID and ORCID_CLIENT_SECRET must be set in environment variables")
        sys.exit(1)
    
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': '/read-public'
    }
    
    try:
        print(f"Requesting token from ORCID...")
        response = requests.post(ORCID_TOKEN_URL, data=data)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response body: {response.text}")
        
        response.raise_for_status()
        token_data = response.json()
        print("✓ Token obtained successfully")
        return token_data['access_token']
    except requests.RequestException as e:
        print(f"ERROR: Failed to get access token: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        sys.exit(1)


def fetch_orcid_works(access_token):
    """Fetch all works from ORCID profile."""
    if not ORCID_ID:
        print("ERROR: ORCID_ID must be set in environment variables")
        sys.exit(1)
    
    url = f'{ORCID_API_BASE}/{ORCID_ID}/works'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        print(f"Fetching works from: {url}")
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response body: {response.text}")
        
        response.raise_for_status()
        works = response.json()
        print(f"✓ Successfully fetched works data")
        return works
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch works from ORCID: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'No response'}")
        sys.exit(1)


def sanitize_filename(title):
    """Create a safe filename from publication title."""
    # Remove special characters and replace spaces with hyphens
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[-\s]+', '-', safe_title)
    return safe_title[:100].strip('-').lower()  # Limit length


def extract_publication_info(work_summary):
    """Extract relevant information from a work summary."""
    title_obj = work_summary.get('title', {})
    title = title_obj.get('title', {}).get('value', 'Untitled')
    
    # Extract publication date
    pub_date = work_summary.get('publication-date')
    if pub_date:
        year_obj = pub_date.get('year')
        year = year_obj.get('value', '') if year_obj else ''
        
        month_obj = pub_date.get('month')
        month = month_obj.get('value', '01') if month_obj else '01'
        
        day_obj = pub_date.get('day')
        day = day_obj.get('value', '01') if day_obj else '01'
    else:
        year = ''
        month = '01'
        day = '01'
    
    # Create date string
    if year:
        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Extract work type
    work_type = work_summary.get('type', 'other')
    category_info = CATEGORY_MAPPING.get(work_type, {'category': 'manuscripts', 'display': 'Other Works'})
    
    # Extract journal/venue
    journal_title = work_summary.get('journal-title', {}).get('value', '') if work_summary.get('journal-title') else ''
    
    # Extract DOI
    external_ids = work_summary.get('external-ids', {}).get('external-id', [])
    doi = ''
    url = ''
    for ext_id in external_ids:
        if ext_id.get('external-id-type') == 'doi':
            doi = ext_id.get('external-id-value', '')
            url = f"https://doi.org/{doi}"
            break
        elif ext_id.get('external-id-type') == 'uri':
            url = ext_id.get('external-id-value', '')
    
    # Extract authors (simplified - ORCID API may require additional calls for full details)
    # For now, we'll use a placeholder that can be manually edited
    citation = f"Citation information from ORCID (Work Type: {work_type})"
    
    return {
        'title': title,
        'date': date_str,
        'year': year,
        'category': category_info['category'],
        'work_type': work_type,
        'venue': journal_title,
        'doi': doi,
        'url': url,
        'citation': citation
    }


def generate_markdown_file(pub_info, output_dir):
    """Generate a Jekyll markdown file for a publication."""
    filename = f"{pub_info['date']}-{sanitize_filename(pub_info['title'])}.md"
    filepath = output_dir / filename
    
    # Create permalink
    permalink = f"/publication/{pub_info['date']}-{sanitize_filename(pub_info['title'])}"
    
    # Generate excerpt (first 200 chars of title or custom)
    excerpt = pub_info['title'][:200] + '...' if len(pub_info['title']) > 200 else pub_info['title']
    
    # Create markdown content
    content = f"""---
title: "{pub_info['title']}"
collection: publications
category: {pub_info['category']}
permalink: {permalink}
excerpt: '{excerpt}'
date: {pub_info['date']}
venue: '{pub_info['venue']}'
"""
    
    if pub_info['url']:
        content += f"paperurl: '{pub_info['url']}'\n"
    
    if pub_info['doi']:
        content += f"doi: '{pub_info['doi']}'\n"
    
    content += f"citation: '{pub_info['citation']}'\n"
    content += "---\n\n"
    
    # Add work type information
    work_type_display = {
        'journal-article': 'Journal Article',
        'working-paper': 'Working Paper',
        'preprint': 'Preprint',
        'conference-paper': 'Conference Paper',
        'book-chapter': 'Book Chapter',
        'book': 'Book',
        'dissertation': 'Dissertation',
        'report': 'Report',
    }
    
    content += f"**Type**: {work_type_display.get(pub_info['work_type'], pub_info['work_type'])}\n\n"
    
    if pub_info['venue']:
        content += f"**Published in**: {pub_info['venue']}\n\n"
    
    if pub_info['doi']:
        content += f"**DOI**: [{pub_info['doi']}](https://doi.org/{pub_info['doi']})\n\n"
    
    content += "## Abstract\n\n"
    content += "*This publication was automatically imported from ORCID. Please edit this file to add abstract and additional details.*\n"
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Generated: {filename}")
    return filename


def main():
    """Main execution function."""
    print("=" * 60)
    print("ORCID Publications Importer")
    print("=" * 60)
    
    # Validate configuration
    if not ORCID_ID:
        print("\n⚠ WARNING: ORCID_ID not set. Using test mode.")
        print("Please set the ORCID_ID environment variable.")
        print("\nFor GitHub Actions, add these secrets:")
        print("  - ORCID_ID: Your ORCID ID (e.g., 0000-0002-1234-5678)")
        print("  - ORCID_CLIENT_ID: Your ORCID API client ID")
        print("  - ORCID_CLIENT_SECRET: Your ORCID API client secret")
        sys.exit(1)
    
    print(f"\nORCID ID: {ORCID_ID}")
    
    # Get access token
    print("\nAuthenticating with ORCID API...")
    access_token = get_access_token()
    print("✓ Authentication successful")
    
    # Fetch works
    print("\nFetching publications from ORCID...")
    works_data = fetch_orcid_works(access_token)
    
    # Parse works
    groups = works_data.get('group', [])
    print(f"✓ Found {len(groups)} publication(s)")
    
    # Create output directory
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / '_publications'
    output_dir.mkdir(exist_ok=True)
    
    print(f"\nGenerating markdown files in {output_dir}...")
    
    # Process each work
    generated_files = []
    working_papers = []
    published_works = []
    
    for group in groups:
        work_summaries = group.get('work-summary', [])
        if work_summaries:
            work_summary = work_summaries[0]  # Use first summary
            pub_info = extract_publication_info(work_summary)
            
            # Categorize
            if pub_info['category'] == 'working-papers':
                working_papers.append(pub_info)
            else:
                published_works.append(pub_info)
            
            # Generate markdown file
            filename = generate_markdown_file(pub_info, output_dir)
            generated_files.append(filename)
    
    # Summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Total publications imported: {len(generated_files)}")
    print(f"  - Published works: {len(published_works)}")
    print(f"  - Working papers: {len(working_papers)}")
    print("\n✓ Import completed successfully!")
    print("\nNext steps:")
    print("1. Review generated files in _publications/ directory")
    print("2. Edit files to add abstracts and additional details")
    print("3. Commit and push changes to GitHub")


if __name__ == '__main__':
    main()
