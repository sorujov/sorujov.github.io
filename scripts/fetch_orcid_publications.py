#!/usr/bin/env python3
"""
Fetch publications from ORCID API and generate Jekyll markdown files.
Credentials are stored securely in environment variables (GitHub Secrets).

Features:
  - Creates new publication files for newly found works
  - Updates existing files when ORCID metadata changes (preserving manual edits)
  - Retries failed API calls with exponential backoff
  - Fetches abstracts from ORCID, CrossRef, and SSRN
"""

import os
import sys
import json
import html
import time
import hashlib
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

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubled each retry

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


def request_with_retry(method, url, max_retries=MAX_RETRIES, **kwargs):
    """Make an HTTP request with retry and exponential backoff."""
    last_exception = None
    for attempt in range(max_retries):
        try:
            response = method(url, **kwargs)
            if response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get('Retry-After', RETRY_BACKOFF * (2 ** attempt)))
                print(f"  ⏳ Rate limited, waiting {retry_after}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_after)
                continue
            if response.status_code >= 500:  # Server error, retry
                wait = RETRY_BACKOFF * (2 ** attempt)
                print(f"  ⏳ Server error {response.status_code}, retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait)
                continue
            return response
        except requests.RequestException as e:
            last_exception = e
            wait = RETRY_BACKOFF * (2 ** attempt)
            print(f"  ⏳ Request failed: {e}, retrying in {wait}s (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)
    # Return last response or raise
    if last_exception:
        raise last_exception
    return response


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
        response = request_with_retry(requests.post, ORCID_TOKEN_URL, data=data, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response body: {response.text}")
        
        response.raise_for_status()
        token_data = response.json()
        print("✓ Token obtained successfully")
        return token_data['access_token']
    except requests.RequestException as e:
        print(f"ERROR: Failed to get access token: {e}")
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
        response = request_with_retry(requests.get, url, headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Response body: {response.text}")
        
        response.raise_for_status()
        works = response.json()
        print(f"✓ Successfully fetched works data")
        return works
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch works from ORCID: {e}")
        sys.exit(1)


def fetch_work_details(put_code, access_token):
    """Fetch detailed information for a specific work including abstract."""
    url = f'{ORCID_API_BASE}/{ORCID_ID}/work/{put_code}'
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = request_with_retry(requests.get, url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠ Could not fetch details for work {put_code} (status: {response.status_code})")
            return None
    except requests.RequestException as e:
        print(f"⚠ Error fetching work details for {put_code}: {e}")
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
        response = request_with_retry(requests.get, url, max_retries=2, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', {})
            abstract = message.get('abstract')
            if abstract:
                abstract = html.unescape(abstract)
                abstract = re.sub(r'<[^>]+>', '', abstract)
                return abstract.strip()
        return None
    except Exception:
        return None


def fetch_abstract_from_ssrn(doi):
    """Fetch abstract from SSRN by parsing the paper page."""
    if not doi or 'ssrn' not in doi.lower():
        return None
    
    try:
        ssrn_id = doi.split('ssrn.')[-1]
        url = f'https://papers.ssrn.com/sol3/papers.cfm?abstract_id={ssrn_id}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = request_with_retry(requests.get, url, max_retries=2, headers=headers, timeout=15)
        if response.status_code == 200:
            html_content = response.text
            
            abstract_patterns = [
                r'<meta name="description" content="([^"]+)"',
                r'<div[^>]*class="[^"]*abstract-text[^"]*"[^>]*>(.+?)</div>',
                r'<h2[^>]*>Abstract</h2>\s*<p>(.+?)</p>',
            ]
            
            for pattern in abstract_patterns:
                match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
                if match:
                    abstract = match.group(1)
                    abstract = html.unescape(abstract)
                    abstract = re.sub(r'<[^>]+>', '', abstract)
                    abstract = re.sub(r'\s+', ' ', abstract).strip()
                    
                    if len(abstract) > 100:
                        return abstract
        
        return None
    except Exception:
        return None


def parse_existing_frontmatter(filepath):
    """Parse frontmatter from an existing markdown file, returning fields dict and body."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠ Could not read {filepath}: {e}")
        return None, None

    # Split frontmatter and body
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not fm_match:
        return None, content

    fm_text = fm_match.group(1)
    body = fm_match.group(2)

    fields = {}
    for line in fm_text.split('\n'):
        m = re.match(r'^(\w[\w-]*):\s*(.*)', line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            # Strip surrounding quotes
            if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
                val = val[1:-1]
            fields[key] = val

    return fields, body


def get_existing_publications(output_dir):
    """Scan existing publication files and return registries keyed by put-code, DOI, and title.
    
    Each registry maps to a dict with 'filename' and 'fields' (parsed frontmatter).
    """
    existing_putcodes = {}
    existing_dois = {}
    existing_titles = {}
    output_path = Path(output_dir)
    
    if not output_path.exists():
        return existing_putcodes, existing_dois, existing_titles
    
    for md_file in output_path.glob('*.md'):
        fields, body = parse_existing_frontmatter(md_file)
        if fields is None:
            continue

        entry = {'filename': md_file.name, 'filepath': md_file, 'fields': fields, 'body': body}

        putcode = fields.get('orcid_putcode', '')
        if putcode:
            existing_putcodes[putcode] = entry

        doi = fields.get('doi', '')
        if doi:
            existing_dois[doi] = entry

        title = fields.get('title', '').lower().strip()
        if title:
            normalized = re.sub(r'[^\w\s]', '', title)
            normalized = re.sub(r'\s+', ' ', normalized).strip()
            existing_titles[normalized] = entry
    
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
    
    abstract = ''
    paper_url = ''
    
    # Try ORCID first - check multiple possible fields
    if work_details:
        orcid_url = work_details.get('url')
        if orcid_url:
            paper_url = orcid_url if isinstance(orcid_url, str) else orcid_url.get('value', '')
            if paper_url:
                print(f"  ✓ Found paper URL from ORCID: {paper_url}")
        
        short_desc = work_details.get('short-description')
        if short_desc:
            abstract = short_desc if isinstance(short_desc, str) else short_desc.get('value', '')
            if abstract:
                print(f"  ✓ Found abstract from ORCID (short-description)")
        
        if not abstract:
            work_obj = work_details.get('work')
            if work_obj:
                short_desc = work_obj.get('short-description')
                if short_desc:
                    abstract = short_desc if isinstance(short_desc, str) else short_desc.get('value', '')
                    if abstract:
                        print(f"  ✓ Found abstract from ORCID (work.short-description)")
        
        if not abstract:
            desc = work_details.get('description')
            if desc:
                abstract = desc if isinstance(desc, str) else desc.get('value', '')
                if abstract:
                    print(f"  ✓ Found abstract from ORCID (description)")
        
        if not abstract:
            print(f"  ⚠ No abstract in ORCID work details. Available keys: {list(work_details.keys())}")
    
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
    
    # Extract publication date (prefer publication-date, fallback to created-date)
    year = ''
    month = '01'
    day = '01'
    
    pub_date = work_summary.get('publication-date')
    if pub_date:
        year_obj = pub_date.get('year')
        year = year_obj.get('value', '') if year_obj else ''
        
        month_obj = pub_date.get('month')
        month = month_obj.get('value', '01') if month_obj else '01'
        
        day_obj = pub_date.get('day')
        day = day_obj.get('value', '01') if day_obj else '01'
    
    # Fallback: try created-date from work_details (timestamp in ms)
    if not year and work_details:
        created_date = work_details.get('created-date')
        if created_date:
            timestamp_ms = created_date.get('value') if isinstance(created_date, dict) else created_date
            if timestamp_ms:
                try:
                    timestamp_sec = int(timestamp_ms) / 1000
                    date_obj = datetime.fromtimestamp(timestamp_sec)
                    year = str(date_obj.year)
                    month = str(date_obj.month).zfill(2)
                    day = str(date_obj.day).zfill(2)
                    print(f"  ✓ Using created-date as fallback: {year}-{month}-{day}")
                except (ValueError, TypeError) as e:
                    print(f"  ⚠ Could not parse created-date: {e}")
    
    if year:
        date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Extract work type
    work_type = work_summary.get('type', 'other')
    category_info = CATEGORY_MAPPING.get(work_type, {'category': 'manuscripts', 'display': 'Other Works'})
    
    # Extract journal/venue
    journal_title = work_summary.get('journal-title', {}).get('value', '') if work_summary.get('journal-title') else ''
    
    # Extract DOI and URL from external IDs
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
    
    citation = f"Citation information from ORCID (Work Type: {work_type})"
    
    # Compute a fingerprint of the ORCID data so we can detect changes
    fingerprint_data = f"{title}|{date_str}|{work_type}|{journal_title}|{doi}|{paper_url or url}|{abstract}"
    fingerprint = hashlib.md5(fingerprint_data.encode('utf-8')).hexdigest()
    
    # Get last-modified from ORCID if available
    last_modified = ''
    if work_details:
        lm = work_details.get('last-modified-date')
        if lm:
            lm_val = lm.get('value') if isinstance(lm, dict) else lm
            if lm_val:
                try:
                    lm_sec = int(lm_val) / 1000
                    last_modified = datetime.utcfromtimestamp(lm_sec).strftime('%Y-%m-%dT%H:%M:%SZ')
                except (ValueError, TypeError):
                    pass
    
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
        'put_code': put_code,
        'orcid_fingerprint': fingerprint,
        'last_modified': last_modified,
    }


def generate_markdown_file(pub_info, output_dir):
    """Generate a Jekyll markdown file for a publication."""
    filename = f"{pub_info['date']}-{sanitize_filename(pub_info['title'])}.md"
    filepath = output_dir / filename
    
    permalink = f"/publication/{pub_info['date']}-{sanitize_filename(pub_info['title'])}"
    excerpt = pub_info['title'][:200] + '...' if len(pub_info['title']) > 200 else pub_info['title']
    
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
    
    if pub_info.get('github'):
        content += f"github: '{pub_info['github']}'\n"
    
    content += f"citation: '{pub_info['citation']}'\n"
    
    if pub_info.get('orcid_fingerprint'):
        content += f"orcid_fingerprint: '{pub_info['orcid_fingerprint']}'\n"
    
    if pub_info.get('last_modified'):
        content += f"orcid_last_modified: '{pub_info['last_modified']}'\n"
    
    content += "---\n\n"
    
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
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Generated: {filename}")
    return filename


def update_existing_file(pub_info, existing_entry):
    """Update an existing publication file with new ORCID data, preserving manual edits.
    
    Preserved fields (never overwritten if already set by user):
      - github
      - Any field not coming from ORCID
    
    Updated fields (always synced from ORCID):
      - title, category, date, venue, doi, paperurl, citation, abstract,
        orcid_fingerprint, orcid_last_modified
    """
    filepath = existing_entry['filepath']
    old_fields = existing_entry['fields']
    
    # Preserve manually-added fields that ORCID doesn't provide
    preserved_keys = {'github'}
    
    permalink = f"/publication/{pub_info['date']}-{sanitize_filename(pub_info['title'])}"
    excerpt = pub_info['title'][:200] + '...' if len(pub_info['title']) > 200 else pub_info['title']
    
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
    
    # Preserve manually-added fields
    for key in preserved_keys:
        if key in old_fields and old_fields[key]:
            content += f"{key}: '{old_fields[key]}'\n"
    
    content += f"citation: '{pub_info['citation']}'\n"
    
    if pub_info.get('orcid_fingerprint'):
        content += f"orcid_fingerprint: '{pub_info['orcid_fingerprint']}'\n"
    
    if pub_info.get('last_modified'):
        content += f"orcid_last_modified: '{pub_info['last_modified']}'\n"
    
    content += "---\n\n"
    
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
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated: {filepath.name}")
    return filepath.name


def needs_update(pub_info, existing_entry):
    """Check if an existing publication needs updating based on ORCID data changes."""
    old_fields = existing_entry.get('fields', {})
    
    # Fast path: compare fingerprints if available
    old_fp = old_fields.get('orcid_fingerprint', '')
    new_fp = pub_info.get('orcid_fingerprint', '')
    if old_fp and new_fp:
        return old_fp != new_fp
    
    # Fallback: compare key fields individually
    checks = [
        ('title', pub_info.get('title', '')),
        ('category', pub_info.get('category', '')),
        ('venue', pub_info.get('venue', '')),
        ('doi', pub_info.get('doi', '')),
        ('date', pub_info.get('date', '')),
    ]
    for key, new_val in checks:
        old_val = old_fields.get(key, '')
        if old_val != new_val:
            return True
    
    # Check if abstract appeared where there was none
    old_body = existing_entry.get('body', '')
    has_old_abstract = 'automatically imported from ORCID' not in old_body and '## Abstract' in old_body
    has_new_abstract = bool(pub_info.get('abstract'))
    if has_new_abstract and not has_old_abstract:
        return True
    
    return False


def main():
    """Main execution function."""
    print("=" * 60)
    print("ORCID Publications Importer")
    print("=" * 60)
    
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
    print(f"✓ Found {len(groups)} publication(s) on ORCID")
    
    # Create output directory
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / '_publications'
    output_dir.mkdir(exist_ok=True)
    
    # Get existing publications
    print("\nChecking for existing publications...")
    existing_putcodes, existing_dois, existing_titles = get_existing_publications(output_dir)
    print(f"✓ Found {len(existing_putcodes)} existing publication(s) in repository")
    
    print(f"\nProcessing publications from ORCID...")
    
    generated_files = []
    updated_files = []
    skipped_files = []
    working_papers = []
    published_works = []
    
    for group in groups:
        work_summaries = group.get('work-summary', [])
        if not work_summaries:
            continue

        work_summary = work_summaries[0]
        put_code = str(work_summary.get('put-code'))
        
        title = work_summary.get('title', {}).get('title', {}).get('value', 'Unknown')
        normalized_title = re.sub(r'[^\w\s]', '', title.lower().strip())
        normalized_title = re.sub(r'\s+', ' ', normalized_title).strip()
        
        # Quick extract DOI
        external_ids = work_summary.get('external-ids', {}).get('external-id', [])
        doi = ''
        for ext_id in external_ids:
            if ext_id.get('external-id-type') == 'doi':
                doi = ext_id.get('external-id-value', '')
                break
        
        # Check if publication already exists
        existing_entry = None
        if put_code in existing_putcodes:
            existing_entry = existing_putcodes[put_code]
        elif doi and doi in existing_dois:
            existing_entry = existing_dois[doi]
        elif normalized_title in existing_titles:
            existing_entry = existing_titles[normalized_title]
        
        # Always fetch details so we can compare
        print(f"\n→ Processing: {title[:70]}{'...' if len(title) > 70 else ''}")
        work_details = fetch_work_details(put_code, access_token)
        pub_info = extract_publication_info(work_summary, work_details, doi, put_code)
        
        # Categorize
        if pub_info['category'] == 'working-papers':
            working_papers.append(pub_info)
        else:
            published_works.append(pub_info)
        
        if existing_entry:
            # Check if ORCID data has changed
            if needs_update(pub_info, existing_entry):
                # Preserve manually-added fields, update ORCID-sourced data
                filename = update_existing_file(pub_info, existing_entry)
                updated_files.append(filename)
                print(f"  ↑ Metadata changed — file updated")
            else:
                print(f"  ⊗ Skipping (up to date): {existing_entry['filename']}")
                skipped_files.append(title)
        else:
            # New publication
            filename = generate_markdown_file(pub_info, output_dir)
            generated_files.append(filename)
    
    # Summary
    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"Total publications on ORCID: {len(groups)}")
    print(f"  - New publications imported: {len(generated_files)}")
    print(f"  - Existing publications updated: {len(updated_files)}")
    print(f"  - Skipped (already up to date): {len(skipped_files)}")
    print(f"  - Published works: {len(published_works)}")
    print(f"  - Working papers: {len(working_papers)}")
    
    if generated_files:
        print(f"\nNew files:")
        for f in generated_files:
            print(f"  + {f}")
    
    if updated_files:
        print(f"\nUpdated files:")
        for f in updated_files:
            print(f"  ↑ {f}")
    
    print("\n✓ Import completed successfully!")
    
    if not generated_files and not updated_files:
        print("✓ All publications are up to date!")


if __name__ == '__main__':
    main()
