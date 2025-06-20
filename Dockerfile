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
        python3-dev \
        git \
        build-essential \
        && rm -rf /var/lib/apt/lists/*

# Copy all project files into the image
COPY . /workspace

# Ensure requirements.txt is copied and install Python dependencies
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

WORKDIR /workspace
