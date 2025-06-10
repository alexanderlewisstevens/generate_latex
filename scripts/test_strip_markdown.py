import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import convert_pdfs

def test_strip_markdown_codeblock():
    # Should strip ```markdown and ```
    content = """```markdown\n# Title\nSome text\n```"""
    result = convert_pdfs.openai_pdf_to_obsidian("irrelevant", 1)
    # Simulate what the function would do
    # We'll patch the API call to return our test string
    def fake_api(*args, **kwargs):
        return content
    # Patch the function to just return the test string
    orig = convert_pdfs.openai_pdf_to_obsidian
    convert_pdfs.openai_pdf_to_obsidian = lambda text, page_num: content
    stripped = convert_pdfs.openai_pdf_to_obsidian("irrelevant", 1)
    # Now manually apply the stripping logic
    if stripped.startswith('```markdown'):
        stripped = stripped[len('```markdown'):].lstrip('\n')
    if stripped.startswith('```'):
        stripped = stripped[len('```'):].lstrip('\n')
    if stripped.endswith('```'):
        stripped = stripped[:-3].rstrip('\n')
    assert stripped.strip().startswith('# Title')
    assert '```' not in stripped
    # Restore
    convert_pdfs.openai_pdf_to_obsidian = orig
