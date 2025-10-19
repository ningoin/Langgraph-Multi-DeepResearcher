
#!/bin/bash

# Local Deep Researcher Docker Run Script
# This script simplifies running the research assistant in Docker

set -e

# Default values
RESEARCH_TOPIC="${RESEARCH_TOPIC:-人工智能发展趋势}"
OUTPUT_FILE="${OUTPUT_FILE:-research_report.md}"
LLM_PROVIDER="${LLM_PROVIDER:-ollama}"
LOCAL_LLM="${LOCAL_LLM:-llama3}"
SEARCH_API="${SEARCH_API:-duckduckgo}"
MAX_LOOPS="${MAX_LOOPS:-3}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔬 Local Deep Researcher - Docker Runner${NC}"
echo -e "${BLUE}=======================================${NC}"

# Check if required parameters are provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 \"<research_topic>\" [output_file]${NC}"
    echo -e "${YELLOW}Example: $0 \"量子计算最新进展\" quantum_research.md${NC}"
    echo ""
    echo -e "${BLUE}Environment variables:${NC}"
    echo -e "  RESEARCH_TOPIC: ${RESEARCH_TOPIC}"
    echo -e "  OUTPUT_FILE: ${OUTPUT_FILE}"
    echo -e "  LLM_PROVIDER: ${LLM_PROVIDER}"
    echo -e "  LOCAL_LLM: ${LOCAL_LLM}"
    echo -e "  SEARCH_API: ${SEARCH_API}"
    echo -e "  MAX_LOOPS: ${MAX_LOOPS}"
    exit 1
fi

# Override with command line arguments
RESEARCH_TOPIC="$1"
if [ ! -z "$2" ]; then
    OUTPUT_FILE="$2"
fi

echo -e "${GREEN}📋 Research Topic:${NC} ${RESEARCH_TOPIC}"
echo -e "${GREEN}📄 Output File:${NC} ${OUTPUT_FILE}"
echo -e "${GREEN}🤖 LLM Provider:${NC} ${LLM_PROVIDER}"
echo -e "${GREEN}🧠 Model:${NC} ${LOCAL_LLM}"
echo -e "${GREEN}🔍 Search API:${NC} ${SEARCH_API}"
echo -e "${GREEN}🔄 Max Loops:${NC} ${MAX_LOOPS}"
echo ""

# Create output directory if it doesn't exist
mkdir -p output

# Build Docker image if it doesn't exist
if ! docker image inspect local-deep-researcher >/dev/null 2>&1; then
    echo -e "${YELLOW}🔨 Building Docker image...${NC}"
    docker build -t local-deep-researcher .
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
fi

echo -e "${YELLOW}🚀 Starting research...${NC}"
echo ""

# Run the research assistant
docker run --rm -it \
    -e LLM_PROVIDER="${LLM_PROVIDER}" \
    -e LOCAL_LLM="${LOCAL_LLM}" \
    -e OLLAMA_BASE_URL="http://host.docker.internal:11434/" \
    -e SEARCH_API="${SEARCH_API}" \
    -e MAX_WEB_RESEARCH_LOOPS="${MAX_LOOPS}" \
    -e TAVILY_API_KEY="${TAVILY_API_KEY}" \
    -e PERPLEXITY_API_KEY="${PERPLEXITY_API_KEY}" \
    -e OPENAI_API_KEY="${OPENAI_API_KEY}" \
    -v "$(pwd)/output:/app/output" \
    local-deep-researcher \
    --topic "${RESEARCH_TOPIC}" \
    --out "/app/output/${OUTPUT_FILE}" \
    --provider "${LLM_PROVIDER}" \
    --model "${LOCAL_LLM}" \
    --loops "${MAX_LOOPS}" \
    --search "${SEARCH_API}"

echo ""
echo -e "${GREEN}✅ Research completed!${NC}"
echo -e "${GREEN}📄 Report saved to: output/${OUTPUT_FILE}${NC}"
