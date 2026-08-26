FROM python:3.11-slim

# Install common tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    vim \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Default command
CMD ["/bin/bash"]
