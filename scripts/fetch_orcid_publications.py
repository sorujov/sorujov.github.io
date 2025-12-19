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
    """Scan existing publication files and return a registry of put-codes, DOIs, and titles."""
    existing_putcodes = {}
    existing_dois = {}
    existing_titles = {}
    output_path = Path(output_dir)
    
    if not output_path.exists():
        return existing_putcodes, existing_dois, existing_titles
    
    for md_file in output_path.glob('*.md'):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Extract ORCID put-code (unique identifier) - most reliable
                putcode_match = re.search(r'^orcid_putcode:\s*[\'"]?(\d+)[\'"]?', content, re.MULTILINE)
                if putcode_match:
                    putcode = putcode_match.group(1)
                    existing_putcodes[putcode] = md_file.name
                
                # Extract DOI from frontmatter (fallback)
                doi_match = re.search(r'^doi:\s*[\'"](.+?)[\'"]', content, re.MULTILINE)
                if doi_match:
                    doi = doi_match.group(1)
                    existing_dois[doi] = md_file.name
                
                # Extract title for duplicate detection (fallback)
                title_match = re.search(r'^title:\s*[\'"](.+?)[\'"]', content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).lower().strip()
                    # Normalize title: remove punctuation, extra spaces
                    normalized = re.sub(r'[^\w\s]', '', title)
                    normalized = re.sub(r'\s+', ' ', normalized).strip()
                    existing_titles[normalized] = md_file.name
        except Exception as e:
            print(f"⚠ Could not read {md_file.name}: {e}")
    
    return existing_putcodes, existing_dois, existing_titles


def sanitize_filename(title):
    """Create a safe filename from publication title."""
    # Remove special characters and replace spaces with hyphens
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[-\s]+', '-', safe_title)
    return safe_title[:100].strip('-').lower()  # Limit length


def extract_publication_info(work_summary, work_details=None, doi=None, put_code=None):
    """Extract relevant information from a work summary and optionally detailed data."""
    title_obj = work_summary.get('title', {})
    title = title_obj.get('title', {}).get('value', 'Untitled')
    
    # Extract abstract from multiple sources
    abstract = ''
    paper_url = ''
    
    # Try ORCID first - check multiple possible fields
    if work_details:
        # Extract URL from ORCID work details
        orcid_url = work_details.get('url')
        if orcid_url:
            paper_url = orcid_url if isinstance(orcid_url, str) else orcid_url.get('value', '')
            if paper_url:
                print(f"  ✓ Found paper URL from ORCID: {paper_url}")
        
        # Try short-description at root level
        short_desc = work_details.get('short-description')
        if short_desc:
            abstract = short_desc if isinstance(short_desc, str) else short_desc.get('value', '')
            print(f"  ✓ Found abstract from ORCID (short-description)")
        
        # Try work.short-description
        if not abstract:
            work_obj = work_details.get('work')
            if work_obj:
                short_desc = work_obj.get('short-description')
                if short_desc:
                    abstract = short_desc if isinstance(short_desc, str) else short_desc.get('value', '')
                    print(f"  ✓ Found abstract from ORCID (work.short-description)")
        
        # Try description field (alternative name)
        if not abstract:
            desc = work_details.get('description')
            if desc:
                abstract = desc if isinstance(desc, str) else desc.get('value', '')
                print(f"  ✓ Found abstract from ORCID (description)")
        
        # Debug: print available keys if no abstract found
        if not abstract and work_details:
            print(f"  ⚠ No abstract in ORCID work details. Available keys: {list(work_details.keys())}")
            if 'work' in work_details:
                print(f"     Work object keys: {list(work_details['work'].keys())}")
    
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
    
    # Extract publication date - try multiple date fields
    pub_date = work_summary.get('publication-date')
    
    # Check work_details for created-date if available
    created_date = None
    if work_details:
        created_date = work_details.get('created-date')
        if created_date:
            # created-date is in timestamp format, need to convert
            import time
            timestamp_ms = created_date.get('value') if isinstance(created_date, dict) else created_date
            if timestamp_ms:
                try:
                    # Convert milliseconds to seconds
                    timestamp_sec = int(timestamp_ms) / 1000
                    date_obj = datetime.fromtimestamp(timestamp_sec)
                    print(f"  ✓ Found created date from ORCID: {date_obj.strftime('%Y-%m-%d')}")
                    year = str(date_obj.year)
                    month = str(date_obj.month).zfill(2)
                    day = str(date_obj.day).zfill(2)
                except (ValueError, TypeError) as e:
                    print(f"  ⚠ Could not parse created-date: {e}")
                    created_date = None
    
    # If no valid created_date, use publication-date
    if not created_date and pub_date:
        year_obj = pub_date.get('year')
        year = year_obj.get('value', '') if year_obj else ''
        
        month_obj = pub_date.get('month')
        month = month_obj.get('value', '01') if month_obj else '01'
        
        day_obj = pub_date.get('day')
        day = day_obj.get('value', '01') if day_obj else '01'
    elif not created_date:
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
        'paperurl': paper_url if paper_url else url,
        'citation': citation,
        'abstract': abstract,
        'put_code': put_code
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
orcid_putcode: '{pub_info.get('put_code', '')}'
"""
    
    if pub_info.get('paperurl'):
        content += f"paperurl: '{pub_info['paperurl']}'\n"
    
    if pub_info['doi']:
        content += f"doi: '{pub_info['doi']}'\n"
    
    # Add github field if present (will be empty by default, can be manually added)
    if pub_info.get('github'):
        content += f"github: '{pub_info['github']}'\n"
    
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
    existing_putcodes, existing_dois, existing_titles = get_existing_publications(output_dir)
    print(f"✓ Found {len(existing_putcodes)} existing publication(s) in registry")
    
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
            put_code = str(work_summary.get('put-code'))
            
            # Extract title for duplicate checking
            title = work_summary.get('title', {}).get('title', {}).get('value', 'Unknown')
            normalized_title = re.sub(r'[^\w\s]', '', title.lower().strip())
            normalized_title = re.sub(r'\s+', ' ', normalized_title).strip()
            
            # Quick extract DOI to check for duplicates early
            external_ids = work_summary.get('external-ids', {}).get('external-id', [])
            doi = ''
            for ext_id in external_ids:
                if ext_id.get('external-id-type') == 'doi':
                    doi = ext_id.get('external-id-value', '')
                    break
            
            # Check if publication already exists (by put-code first, then DOI, then title)
            if put_code in existing_putcodes:
                print(f"⊗ Skipping: {title[:60]}... (put-code: {put_code}, exists as {existing_putcodes[put_code]})")
                skipped_files.append(title)
                continue
            
            if doi and doi in existing_dois:
                print(f"⊗ Skipping: {title[:60]}... (put-code: {put_code}, exists as {existing_dois[doi]})")
                skipped_files.append(title)
                continue
            
            if normalized_title in existing_titles:
                print(f"⊗ Skipping: {title[:60]}... (put-code: {put_code}, duplicate title, exists as {existing_titles[normalized_title]})")
                skipped_files.append(title)
                continue
            
            # Fetch detailed work information (includes abstract from ORCID)
            work_details = fetch_work_details(put_code, access_token)
            
            # Extract publication info with details (will also try CrossRef for abstract)
            pub_info = extract_publication_info(work_summary, work_details, doi, put_code)
            
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
