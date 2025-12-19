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


def fetch_work_details(put_code, access_token):
    """Fetch detailed information for a specific work including abstract."""
    url = f'{ORCID_API_BASE}/{ORCID_ID}/work/{put_code}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠ Could not fetch details for work {put_code}")
            return None
    except requests.RequestException as e:
        print(f"⚠ Error fetching work details: {e}")
        return None


def fetch_abstract_from_crossref(doi):
    """Fetch abstract from CrossRef API using DOI."""
    if not doi:
        return None
    
    url = f'https://api.crossref.org/works/{doi}'
    headers = {
        'User-Agent': 'ORCID-Publications-Sync/1.0 (mailto:contact@example.com)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', {})
            abstract = message.get('abstract')
            if abstract:
                # CrossRef returns abstract with XML tags, clean them
                import html
                abstract = html.unescape(abstract)
                # Remove XML/HTML tags
                abstract = re.sub(r'<[^>]+>', '', abstract)
                return abstract.strip()
        return None
    except Exception as e:
        # Silently fail - CrossRef is optional
        return None


def fetch_abstract_from_ssrn(doi):
    """Fetch abstract from SSRN by parsing the paper page."""
    if not doi or 'ssrn' not in doi.lower():
        return None
    
    try:
        # Extract SSRN ID from DOI (e.g., 10.2139/ssrn.5920805 -> 5920805)
        ssrn_id = doi.split('ssrn.')[-1]
        url = f'https://papers.ssrn.com/sol3/papers.cfm?abstract_id={ssrn_id}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            html_content = response.text
            
            # Try to find abstract in the HTML
            # SSRN typically has abstract in a specific div or meta tag
            abstract_patterns = [
                r'<meta name="description" content="([^"]+)"',
                r'<div[^>]*class="[^"]*abstract-text[^"]*"[^>]*>(.+?)</div>',
                r'<h2[^>]*>Abstract</h2>\s*<p>(.+?)</p>',
            ]
            
            for pattern in abstract_patterns:
                match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
                if match:
                    abstract = match.group(1)
                    # Clean HTML tags and entities
                    import html
                    abstract = html.unescape(abstract)
                    abstract = re.sub(r'<[^>]+>', '', abstract)
                    abstract = re.sub(r'\s+', ' ', abstract).strip()
                    
                    if len(abstract) > 100:  # Ensure it's a real abstract
                        return abstract
        
        return None
    except Exception as e:
        # Silently fail - SSRN fetching is optional
        return None


def get_existing_publications(output_dir):
    """Scan existing publication files and return a dict of DOI -> filename."""
    existing = {}
    output_path = Path(output_dir)
    
    if not output_path.exists():
        return existing
    
    for md_file in output_path.glob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract DOI from frontmatter
                doi_match = re.search(r'^doi:\s*[\'"](.+?)[\'"]', content, re.MULTILINE)
                if doi_match:
                    doi = doi_match.group(1)
                    existing[doi] = md_file.name
        except Exception as e:
            print(f"⚠ Could not read {md_file.name}: {e}")
    
    return existing


def sanitize_filename(title):
    """Create a safe filename from publication title."""
    # Remove special characters and replace spaces with hyphens
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[-\s]+', '-', safe_title)
    return safe_title[:100].strip('-').lower()  # Limit length


def extract_publication_info(work_summary, work_details=None, doi=None):
    """Extract relevant information from a work summary and optionally detailed data."""
    title_obj = work_summary.get('title', {})
    title = title_obj.get('title', {}).get('value', 'Untitled')
    
    # Extract abstract from multiple sources
    abstract = ''
    
    # Try ORCID first
    if work_details:
        short_desc = work_details.get('short-description')
        if short_desc:
            abstract = short_desc
    
    # If no abstract from ORCID, try SSRN (for SSRN papers)
    if not abstract and doi and 'ssrn' in doi.lower():
        ssrn_abstract = fetch_abstract_from_ssrn(doi)
        if ssrn_abstract:
            abstract = ssrn_abstract
            print(f"  ✓ Found abstract from SSRN")
    
    # If still no abstract, try CrossRef
    if not abstract and doi:
        crossref_abstract = fetch_abstract_from_crossref(doi)
        if crossref_abstract:
            abstract = crossref_abstract
            print(f"  ✓ Found abstract from CrossRef")
    
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
        'citation': citation,
        'abstract': abstract
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
    
    if pub_info.get('abstract'):
        content += f"{pub_info['abstract']}\n\n"
    else:
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
    
    # Get existing publications to avoid duplicates
    print("\nChecking for existing publications...")
    existing_pubs = get_existing_publications(output_dir)
    print(f"✓ Found {len(existing_pubs)} existing publication(s)")
    
    print(f"\nProcessing publications from ORCID...")
    
    # Process each work
    generated_files = []
    skipped_files = []
    working_papers = []
    published_works = []
    
    for group in groups:
        work_summaries = group.get('work-summary', [])
        if work_summaries:
            work_summary = work_summaries[0]  # Use first summary
            put_code = work_summary.get('put-code')
            
            # Quick extract DOI to check for duplicates early
            external_ids = work_summary.get('external-ids', {}).get('external-id', [])
            doi = ''
            for ext_id in external_ids:
                if ext_id.get('external-id-type') == 'doi':
                    doi = ext_id.get('external-id-value', '')
                    break
            
            # Check if publication already exists (by DOI)
            if doi and doi in existing_pubs:
                title = work_summary.get('title', {}).get('title', {}).get('value', 'Unknown')
                print(f"⊗ Skipping: {title[:60]}... (exists as {existing_pubs[doi]})")
                skipped_files.append(title)
                continue
            
            # Fetch detailed work information (includes abstract from ORCID)
            work_details = fetch_work_details(put_code, access_token)
            
            # Extract publication info with details (will also try CrossRef for abstract)
            pub_info = extract_publication_info(work_summary, work_details, doi)
            
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
    print(f"Total publications processed: {len(groups)}")
    print(f"  - New publications imported: {len(generated_files)}")
    print(f"  - Skipped (already exist): {len(skipped_files)}")
    print(f"  - Published works: {len(published_works)}")
    print(f"  - Working papers: {len(working_papers)}")
    print("\n✓ Import completed successfully!")
    if generated_files:
        print("\nNext steps:")
        print("1. Review generated files in _publications/ directory")
        print("2. Edit files to add/enhance abstracts and additional details")
        print("3. Commit and push changes to GitHub")
    else:
        print("\n✓ All publications are up to date!")


if __name__ == '__main__':
    main()
