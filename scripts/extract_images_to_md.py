import fitz  # PyMuPDF
import sys
from pathlib import Path
import re

def extract_images_from_pdf(pdf_path, md_dir):
    pdf = fitz.open(pdf_path)
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        images = page.get_images(full=True)
        if not images:
            continue
        # Markdown file for this page
        md_file = md_dir / f"page_{str(page_num+1).zfill(4)}.md"
        if not md_file.exists():
            continue
        with open(md_file, 'a', encoding='utf-8') as md:
            for i, img in enumerate(images):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                ext = base_image['ext']
                image_bytes = base_image['image']
                # Try to get a meaningful name from the image info or fallback
                name_hint = base_image.get('name', f"img{i+1}")
                # Clean up name_hint for filesystem
                name_hint = re.sub(r'[^a-zA-Z0-9_-]', '_', name_hint)
                image_name = f"page_{str(page_num+1).zfill(4)}_{name_hint}.{ext}"
                image_path = md_dir / image_name
                with open(image_path, 'wb') as imgf:
                    imgf.write(image_bytes)
                # Add standard Markdown image reference at the end of the markdown file
                md.write(f"\n![{image_name}]({image_name})\n")
    print(f"Images extracted and references added to markdown in {md_dir}/")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_images_to_md.py <pdf_path> <md_dir>")
        sys.exit(1)
    pdf_path = Path(sys.argv[1])
    md_dir = Path(sys.argv[2])
    extract_images_from_pdf(pdf_path, md_dir)

if __name__ == "__main__":
    main()
