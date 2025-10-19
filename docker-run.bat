@echo off
setlocal enabledelayedexpansion

REM Local Deep Researcher Docker Run Script for Windows
REM This script simplifies running the research assistant in Docker

REM Default values
if not defined RESEARCH_TOPIC set RESEARCH_TOPIC=人工智能发展趋势
if not defined OUTPUT_FILE set OUTPUT_FILE=research_report.md
if not defined LLM_PROVIDER set LLM_PROVIDER=ollama
if not defined LOCAL_LLM set LOCAL_LLM=llama3
if not defined SEARCH_API set SEARCH_API=duckduckgo
if not defined MAX_LOOPS set MAX_LOOPS=3

echo 🔬 Local Deep Researcher - Docker Runner
echo =======================================

REM Check if required parameters are provided
if "%~1"=="" (
    echo Usage: %0 "research_topic" [output_file]
    echo Example: %0 "量子计算最新进展" quantum_research.md
    echo.
    echo Environment variables:
    echo   RESEARCH_TOPIC: %RESEARCH_TOPIC%
    echo   OUTPUT_FILE: %OUTPUT_FILE%
    echo   LLM_PROVIDER: %LLM_PROVIDER%
    echo   LOCAL_LLM: %LOCAL_LLM%
    echo   SEARCH_API: %SEARCH_API%
    echo   MAX_LOOPS: %MAX_LOOPS%
    exit /b 1
)

REM Override with command line arguments
set RESEARCH_TOPIC=%~1
if not "%~2"=="" set OUTPUT_FILE=%~2

echo 📋 Research Topic: %RESEARCH_TOPIC%
echo 📄 Output File: %OUTPUT_FILE%
echo 🤖 LLM Provider: %LLM_PROVIDER%
echo 🧠 Model: %LOCAL_LLM%
echo 🔍 Search API: %SEARCH_API%
echo 🔄 Max Loops: %MAX_LOOPS%
echo.

REM Create output directory if it doesn't exist
if not exist "output" mkdir output

REM Build Docker image if it doesn't exist
docker image inspect local-deep-researcher >nul 2>&1
if errorlevel 1 (
    echo 🔨 Building Docker image...
    docker build -t local-deep-researcher .
    if errorlevel 1 (
        echo ❌ Failed to build Docker image
        exit /b 1
    )
    echo ✅ Docker image built successfully!
)

echo 🚀 Starting research...
echo.

REM Run the research assistant
docker run --rm -it ^
    -e LLM_PROVIDER=%LLM_PROVIDER% ^
    -e LOCAL_LLM=%LOCAL_LLM% ^
    -e OLLAMA_BASE_URL=http://host.docker.internal:11434/ ^
    -e SEARCH_API=%SEARCH_API% ^
    -e MAX_WEB_RESEARCH_LOOPS=%MAX_LOOPS% ^
    -e TAVILY_API_KEY=%TAVILY_API_KEY% ^
    -e PERPLEXITY_API_KEY=%PERPLEXITY_API_KEY% ^
    -e OPENAI_API_KEY=%OPENAI_API_KEY% ^
    -v "%cd%\output:/app/output" ^
    local-deep-researcher ^
    --topic "%RESEARCH_TOPIC%" ^
    --out "/app/output/%OUTPUT_FILE%" ^
    --provider "%LLM_PROVIDER%" ^
    --model "%LOCAL_LLM%" ^
    --loops "%MAX_LOOPS%" ^
    --search "%SEARCH_API%"

echo.
echo ✅ Research completed!
echo 📄 Report saved to: output\%OUTPUT_FILE%
