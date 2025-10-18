FROM --platform=$BUILDPLATFORM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    rustc \
    cargo \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy the repository content
COPY . /app

# Set default environment variables
# LLM Configuration
ENV LLM_PROVIDER="ollama"
ENV LOCAL_LLM="llama3"
ENV OLLAMA_BASE_URL="http://host.docker.internal:11434/"
ENV OPENAI_BASE_URL="https://api.openai.com/v1"

# Search Configuration
ENV SEARCH_API="duckduckgo"
ENV FETCH_FULL_PAGE="true"

# Research Configuration
ENV MAX_WEB_RESEARCH_LOOPS="3"

# Advanced Options
ENV USE_TOOL_CALLING="false"
ENV STRIP_THINKING_TOKENS="true"

# Install dependencies
RUN pip install --no-cache-dir -e .

# Create output directory for research reports
RUN mkdir -p /app/output

# Set default command to run the research assistant
# Users can override this by providing their own command with --topic and --out parameters
CMD ["python", "-m", "Langgraph_deep_researcher", "--help"]