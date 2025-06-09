# Dockerfile for LaTeX PDF and Markdown generation
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        texlive-full \
        pandoc \
        make \
        python3 \
        python3-pip \
        git \
        && rm -rf /var/lib/apt/lists/*

# Copy only files needed for build (if you add more, add them here)
COPY Makefile main.tex ./

WORKDIR /workspace
