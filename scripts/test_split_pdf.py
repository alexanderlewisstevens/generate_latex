import os
import shutil
import json
import tempfile
import pytest
from PyPDF2 import PdfWriter, PdfReader
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import split_pdf

def create_sample_pdf(path, num_pages=3):
    writer = PdfWriter()
    for i in range(num_pages):
        writer.add_blank_page(width=72, height=72)
    with open(path, "wb") as f:
        writer.write(f)

def test_split_pdf_creates_pages_and_index(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    out_dir = tmp_path / "sample_pages"
    create_sample_pdf(pdf_path, num_pages=5)
    split_pdf.split_pdf(str(pdf_path), str(out_dir))
    # Generate index after splitting
    reader = PdfReader(str(pdf_path))
    split_pdf.generate_index(reader, str(out_dir))
    # Check that 5 page files exist
    page_files = list(out_dir.glob("page_*.pdf"))
    assert len(page_files) == 5
    # Check that index.txt exists and is valid JSON
    index_file = out_dir / "index.txt"
    assert index_file.exists()
    with open(index_file) as f:
        data = json.load(f)
    assert isinstance(data, dict)
    # Check that __all_pages__ key exists and is correct
    assert data["__all_pages__"] == [1, 2, 3, 4, 5]

def test_pad_page_number():
    assert split_pdf.pad_page_number(1, 5) == "0001"
    assert split_pdf.pad_page_number(12, 123) == "0012"
    assert split_pdf.pad_page_number(123, 1234) == "0123"
    assert split_pdf.pad_page_number(1234, 1234) == "1234"

def test_split_pdf(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    out_dir = tmp_path / "pages"
    create_sample_pdf(pdf_path, num_pages=5)
    files = split_pdf.split_pdf(str(pdf_path), str(out_dir))
    assert len(files) == 5
    for i, f in enumerate(files, 1):
        assert os.path.exists(f)
        reader = PdfReader(f)
        assert len(reader.pages) == 1

def test_flatten_outline():
    # Simulate a simple outline tree
    outline = [
        {'title': 'Chapter 1', 'page': 1, 'children': [
            {'title': 'Section 1.1', 'page': 2, 'children': []},
            {'title': 'Section 1.2', 'page': 3, 'children': []}
        ]},
        {'title': 'Chapter 2', 'page': 4, 'children': []}
    ]
    flat = split_pdf.flatten_outline(outline)
    assert flat['Chapter 1'] == [1]
    assert flat['Chapter 1 > Section 1.1'] == [2]
    assert flat['Chapter 1 > Section 1.2'] == [3]
    assert flat['Chapter 2'] == [4]

def test_flatten_outline_simple():
    outline = [
        {"title": "Chapter 1", "page": 1, "children": [
            {"title": "Section 1.1", "page": 2, "children": []}
        ]}
    ]
    flat = split_pdf.flatten_outline(outline)
    assert "Chapter 1" in flat
    assert "Chapter 1 > Section 1.1" in flat
    assert flat["Chapter 1"] == [1]
    assert flat["Chapter 1 > Section 1.1"] == [2]

def test_extract_outline_blank():
    # Should handle PDFs with no outline gracefully
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        create_sample_pdf(f.name, num_pages=2)
        reader = PdfReader(f.name)
        outline = split_pdf.extract_outline(reader)
        assert isinstance(outline, list)
        assert outline == []

def test_extract_outline_handles_no_outline(tmp_path):
    pdf_path = tmp_path / "no_outline.pdf"
    create_sample_pdf(pdf_path, num_pages=2)
    reader = PdfReader(str(pdf_path))
    outline = split_pdf.extract_outline(reader)
    assert isinstance(outline, list)
    assert outline == []

def test_main(tmp_path, monkeypatch):
    pdf_path = tmp_path / "test.pdf"
    create_sample_pdf(pdf_path, num_pages=2)
    out_dir = tmp_path / "pages"
    # Patch sys.argv
    monkeypatch.setattr(split_pdf.sys, 'argv', ['split_pdf.py', str(pdf_path), str(out_dir)])
    split_pdf.main()
    # Check output
    assert os.path.isdir(out_dir)
    assert os.path.exists(out_dir / "index.txt")
    with open(out_dir / "index.txt") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    # Should have 2 page files
    page_files = list(out_dir.glob("page_*.pdf"))
    assert len(page_files) == 2
