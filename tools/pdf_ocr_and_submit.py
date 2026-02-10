"""PDF OCR -> text/table/image extraction -> submit to LightRAG upload endpoint.

Requirements (Windows):
- Install Tesseract OCR and add to PATH (https://github.com/tesseract-ocr/tesseract)
- Install poppler and add to PATH (for pdf2image)
- Python packages: pip install pytesseract pdf2image pdfplumber requests pandas pillow

This script will:
1. Try to extract selectable text and tables with pdfplumber.
2. If no text, rasterize pages with pdf2image and run pytesseract OCR (Korean + English).
3. Extract images from PDF pages and save them separately.
4. Merge extracted text and table CSVs into a single .txt file.
5. POST the original PDF file to LightRAG `/documents/upload` (server must be running).
"""
import os
import sys
import tempfile
import pdfplumber
from pdf2image import convert_from_path
import pytesseract
import requests
import pandas as pd
from PIL import Image

LIGHTRAG_UPLOAD_URL = os.environ.get("LIGHTRAG_UPLOAD_URL", "http://127.0.0.1:9621/documents/upload")

def extract_with_pdfplumber(pdf_path):
    text_parts = []
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                text_parts.append(txt)
            page_tables = page.extract_tables()
            for t in page_tables:
                df = pd.DataFrame(t[1:], columns=t[0]) if len(t) > 1 else pd.DataFrame(t)
                tables.append(df)
    return "\n\n".join(text_parts), tables

def ocr_with_pytesseract(pdf_path):
    text_parts = []
    images = convert_from_path(pdf_path)
    for img in images:
        txt = pytesseract.image_to_string(img, lang='kor+eng')
        text_parts.append(txt)
    return "\n\n".join(text_parts)

def save_tables_as_csv(tables, out_dir):
    paths = []
    for i, df in enumerate(tables):
        p = os.path.join(out_dir, f"table_{i}.csv")
        df.to_csv(p, index=False, encoding='utf-8-sig')
        paths.append(p)
    return paths

def extract_images_from_pdf(pdf_path, out_dir):
    """Extract images from PDF pages and save them."""
    image_paths = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                images = page.images
                for img_num, img_obj in enumerate(images):
                    try:
                        # Get image bbox and crop
                        x0, top, x1, bottom = img_obj['x0'], img_obj['top'], img_obj['x1'], img_obj['bottom']
                        img = page.within_bbox((x0, top, x1, bottom)).to_image()
                        img_path = os.path.join(out_dir, f"page{page_num}_img{img_num}.png")
                        img.save(img_path)
                        image_paths.append(img_path)
                    except Exception as e:
                        print(f"Warning: Failed to extract image {img_num} from page {page_num}: {e}")
    except Exception as e:
        print(f"Warning: Image extraction failed: {e}")
    return image_paths

def submit_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        files = {'file': (os.path.basename(pdf_path), f, 'application/pdf')}
        r = requests.post(LIGHTRAG_UPLOAD_URL, files=files)
        return r

def process_and_submit(pdf_path, extract_images=True):
    """
    Process PDF: extract text, tables, and optionally images.
    Then submit to LightRAG.
    """
    print(f"Processing: {pdf_path}")
    text, tables = extract_with_pdfplumber(pdf_path)

    if not text.strip():
        print("No selectable text, running OCR (Korean + English)...")
        text = ocr_with_pytesseract(pdf_path)
    else:
        print("Extracted selectable text via pdfplumber.")

    with tempfile.TemporaryDirectory() as td:
        # Save extracted text
        txt_path = os.path.join(td, "extracted.txt")
        with open(txt_path, 'w', encoding='utf-8') as wf:
            wf.write("=" * 80 + "\n")
            wf.write("EXTRACTED TEXT\n")
            wf.write("=" * 80 + "\n\n")
            wf.write(text)
            wf.write('\n\n')

        # Save tables
        csv_paths = []
        if tables:
            csv_paths = save_tables_as_csv(tables, td)
            print(f"Saved {len(csv_paths)} table(s) as CSV")
            with open(txt_path, 'a', encoding='utf-8') as wf:
                wf.write("=" * 80 + "\n")
                wf.write("EXTRACTED TABLES\n")
                wf.write("=" * 80 + "\n\n")
                for i, csv_path in enumerate(csv_paths):
                    wf.write(f"\n--- Table {i+1} ---\n")
                    with open(csv_path, 'r', encoding='utf-8-sig') as cf:
                        wf.write(cf.read())
                    wf.write('\n')

        # Extract images (optional)
        image_paths = []
        if extract_images:
            print("Extracting images from PDF...")
            image_paths = extract_images_from_pdf(pdf_path, td)
            if image_paths:
                print(f"Extracted {len(image_paths)} image(s)")

        print(f"\nExtraction summary:")
        print(f"  - Text: {len(text)} characters")
        print(f"  - Tables: {len(tables)}")
        print(f"  - Images: {len(image_paths)}")

        print("\nSubmitting original PDF to LightRAG upload endpoint...")
        resp = submit_pdf(pdf_path)
        print("Response:", resp.status_code, resp.text[:400] if resp.text else "")
        return resp.status_code == 200

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python tools/pdf_ocr_and_submit.py <file.pdf>")
        sys.exit(1)
    pdf = sys.argv[1]
    ok = process_and_submit(pdf)
    if ok:
        print("Submitted successfully")
    else:
        print("Submit failed")
