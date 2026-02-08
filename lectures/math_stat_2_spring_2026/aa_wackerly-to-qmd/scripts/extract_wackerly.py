#!/usr/bin/env python3
"""
Extract content from Wackerly Mathematical Statistics PDF.

Usage:
    python extract_wackerly.py <pdf_path> <start_page> <end_page> [--images]
    
Examples:
    # Extract Chapter 6 text (pages 320-369)
    python extract_wackerly.py /path/to/wackerly.pdf 320 369
    
    # Extract with images
    python extract_wackerly.py /path/to/wackerly.pdf 320 325 --images
"""

import sys
import os

def extract_text(pdf_path, start_page, end_page):
    """Extract text from specified page range."""
    import fitz
    doc = fitz.open(pdf_path)
    
    text_content = []
    for page_num in range(start_page - 1, min(end_page, doc.page_count)):
        page = doc[page_num]
        text = page.get_text()
        # Clean up common OCR artifacts
        text = text.replace('\n\n\n', '\n\n')
        text_content.append(f"\n{'='*60}\nPAGE {page_num + 1}\n{'='*60}\n{text}")
    
    doc.close()
    return '\n'.join(text_content)

def extract_images(pdf_path, start_page, end_page, output_dir):
    """Extract images from specified page range."""
    import fitz
    doc = fitz.open(pdf_path)
    
    os.makedirs(output_dir, exist_ok=True)
    image_count = 0
    
    for page_num in range(start_page - 1, min(end_page, doc.page_count)):
        page = doc[page_num]
        images = page.get_images()
        
        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_path = os.path.join(output_dir, f"page{page_num+1}_img{img_index+1}.{image_ext}")
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            image_count += 1
            print(f"Extracted: {image_path}")
    
    doc.close()
    return image_count

def get_chapter_pages():
    """Return dictionary of chapter start pages."""
    return {
        1: (25, 43),    # What Is Statistics?
        2: (44, 109),   # Probability
        3: (110, 180),  # Discrete Random Variables
        4: (181, 246),  # Continuous Variables
        5: (247, 319),  # Multivariate Probability Distributions
        6: (320, 369),  # Functions of Random Variables
        7: (370, 413),  # Sampling Distributions and CLT
        8: (414, 467),  # Estimation
        9: (468, 511),  # Properties of Point Estimators
        10: (512, 586), # Hypothesis Testing
        11: (587, 663), # Linear Models
        12: (664, 684), # Designing Experiments
        13: (685, 736), # Analysis of Variance
        14: (737, 764), # Categorical Data
        15: (765, 819), # Nonparametric Statistics
        16: (820, 844), # Bayesian Methods
    }

def extract_chapter(pdf_path, chapter_num, output_file=None, include_images=False):
    """Extract a complete chapter."""
    chapters = get_chapter_pages()
    
    if chapter_num not in chapters:
        print(f"Error: Chapter {chapter_num} not found. Valid chapters: 1-16")
        return None
    
    start_page, end_page = chapters[chapter_num]
    print(f"Extracting Chapter {chapter_num}: pages {start_page}-{end_page}")
    
    text = extract_text(pdf_path, start_page, end_page)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text saved to: {output_file}")
    
    if include_images:
        img_dir = f"chapter{chapter_num}_images"
        count = extract_images(pdf_path, start_page, end_page, img_dir)
        print(f"Extracted {count} images to: {img_dir}/")
    
    return text

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Check if extracting by chapter number
    if sys.argv[2].startswith('ch'):
        chapter_num = int(sys.argv[2][2:])
        include_images = '--images' in sys.argv
        extract_chapter(pdf_path, chapter_num, f"chapter{chapter_num}.txt", include_images)
    else:
        start_page = int(sys.argv[2])
        end_page = int(sys.argv[3])
        include_images = '--images' in sys.argv
        
        text = extract_text(pdf_path, start_page, end_page)
        print(text)
        
        if include_images:
            extract_images(pdf_path, start_page, end_page, "extracted_images")
