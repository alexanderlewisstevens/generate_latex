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

# Copy all project files into the image
COPY . /workspace

WORKDIR /workspace
