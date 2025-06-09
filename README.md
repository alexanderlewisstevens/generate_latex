# generate_latex

This project provides a self-contained workflow to generate PDF and Markdown documents from a LaTeX source file using a Makefile. The Docker image includes all dependencies and project files, so you can build outputs anywhere Docker runs—no local installations required.

## Usage (with Docker)

### 1. Build the Docker image
From the project directory, run:
```sh
docker build -t generate_latex .
```

### 2. Run the build inside the container
To generate both PDF and Markdown outputs:
```sh
docker run --rm -w /workspace generate_latex make all
```

- Outputs (`main.pdf`, `main.md`) will be created inside the container at `/workspace`.
- To copy outputs to your host, use a volume mount. For example:
  ```sh
  docker run --rm -v "$PWD:/workspace" -w /workspace generate_latex make all
  ```
  This will write the outputs to your local directory.

## File Overview
- `main.tex`: Example LaTeX source file.
- `Makefile`: Build instructions for PDF and Markdown outputs.
- `Dockerfile`: Container setup for all dependencies and project files.

## Makefile Targets
- `make pdf`   – Generate PDF from `main.tex` using `pdflatex`
- `make md`    – Generate Markdown from `main.tex` using `pandoc`
- `make all`   – Generate both PDF and Markdown
- `make clean` – Remove all generated files

---
No local LaTeX or Pandoc installation is required—everything runs inside the Docker container.