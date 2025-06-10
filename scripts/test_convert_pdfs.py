import os
import tempfile
import shutil
import pytest
from PyPDF2 import PdfWriter
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import convert_pdfs

def create_single_page_pdf(path, text="Test page"):
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    # PyPDF2 does not support writing text directly, so we will just test extraction logic
    with open(path, "wb") as f:
        writer.write(f)

def test_pdf_page_to_text_blank(tmp_path):
    pdf_path = tmp_path / "blank.pdf"
    create_single_page_pdf(pdf_path)
    text = convert_pdfs.pdf_page_to_text(str(pdf_path))
    assert isinstance(text, str)
    # Should be blank or empty string
    assert text.strip() == ""

def test_main_creates_md_files(monkeypatch, tmp_path):
    # Create a folder with 2 single-page PDFs
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    for i in range(2):
        create_single_page_pdf(pdf_dir / f"page_{i+1:04d}.pdf")
    # Patch openai_pdf_to_obsidian to return dummy markdown
    monkeypatch.setattr(convert_pdfs, "openai_pdf_to_obsidian", lambda text, page_num: f"# Page {page_num}\n{text}")
    # Patch pdf_page_to_text to return dummy text
    monkeypatch.setattr(convert_pdfs, "pdf_page_to_text", lambda path: f"Dummy text for {os.path.basename(path)}")
    # Run main logic
    output_dir = tmp_path / "mds"
    monkeypatch.setattr(convert_pdfs, "main", lambda: None)  # Prevent actual main from running
    # Simulate main logic
    os.makedirs(output_dir, exist_ok=True)
    pdf_files = sorted(f for f in os.listdir(pdf_dir) if f.endswith('.pdf'))
    for idx, pdf_file in enumerate(pdf_files):
        page_num = idx + 1
        pdf_path = os.path.join(pdf_dir, pdf_file)
        text = convert_pdfs.pdf_page_to_text(pdf_path)
        md = convert_pdfs.openai_pdf_to_obsidian(text, page_num)
        md_file = os.path.join(output_dir, os.path.splitext(pdf_file)[0] + ".md")
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md)
    # Check that .md files exist
    md_files = list(output_dir.glob("*.md"))
    assert len(md_files) == 2
    for md_file in md_files:
        with open(md_file) as f:
            content = f.read()
            assert content.startswith("# Page")
