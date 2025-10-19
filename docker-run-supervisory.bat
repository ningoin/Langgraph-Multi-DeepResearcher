@echo off
REM 主管架构系统便捷运行脚本 (Windows 版本)

setlocal enabledelayedexpansion

REM 设置颜色 (Windows 10+ 支持)
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "RED=%ESC%[31m"
set "BLUE=%ESC%[34m"
set "NC=%ESC%[0m"

REM 打印带颜色的消息
:print_message
echo %GREEN%[INFO]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%[WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%[ERROR]%NC% %~1
goto :eof

:print_header
echo %BLUE%================================%NC%
echo %BLUE%  主管架构研究系统%NC%
echo %BLUE%================================%NC%
goto :eof

REM 检查 Docker 是否运行
:check_docker
docker info >nul 2>&1
if %errorlevel% neq 0 (
    call :print_error "Docker 未运行，请先启动 Docker"
    exit /b 1
)
call :print_message "Docker 运行正常"
exit /b 0

REM 检查 Ollama 服务
:check_ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    call :print_warning "Ollama 服务未运行，将使用 Docker 启动"
    exit /b 1
)
call :print_message "Ollama 服务运行正常"
exit /b 0

REM 启动 Ollama 服务
:start_ollama
call :print_message "启动 Ollama 服务..."
docker-compose -f docker-compose-supervisory.yml up -d ollama

REM 等待 Ollama 启动
call :print_message "等待 Ollama 服务启动..."
set /a count=0
:wait_ollama
set /a count+=1
if !count! gtr 30 (
    call :print_error "Ollama 服务启动超时"
    exit /b 1
)
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 2 >nul
    goto :wait_ollama
)
call :print_message "Ollama 服务已启动"
exit /b 0

REM 下载模型
:download_model
set "model=%~1"
if "%model%"=="" set "model=llama3"
call :print_message "检查模型 %model% 是否已下载..."

curl -s http://localhost:11434/api/tags | findstr /C:"\"name\":\"%model%\"" >nul
if %errorlevel% equ 0 (
    call :print_message "模型 %model% 已存在"
    exit /b 0
)

call :print_message "下载模型 %model%..."
docker exec ollama-supervisory ollama pull %model%

if %errorlevel% equ 0 (
    call :print_message "模型 %model% 下载完成"
) else (
    call :print_error "模型 %model% 下载失败"
    exit /b 1
)
exit /b 0

REM 运行主管架构研究
:run_supervisory_research
set "topic=%~1"
set "output_file=%~2"
if "%output_file%"=="" set "output_file=supervisory_research_report.md"
set "provider=%~3"
if "%provider%"=="" set "provider=ollama"
set "model=%~4"
if "%model%"=="" set "model=llama3"
set "search_api=%~5"
if "%search_api%"=="" set "search_api=duckduckgo"
set "max_loops=%~6"
if "%max_loops%"=="" set "max_loops=3"

call :print_message "开始主管架构研究..."
call :print_message "主题: %topic%"
call :print_message "输出文件: %output_file%"
call :print_message "LLM 提供商: %provider%"
call :print_message "模型: %model%"
call :print_message "搜索引擎: %search_api%"
call :print_message "最大循环次数: %max_loops%"

REM 创建输出目录
if not exist "output" mkdir output

REM 运行研究
docker-compose -f docker-compose-supervisory.yml run --rm -e RESEARCH_TOPIC="%topic%" supervisory-researcher python -m Langgraph_deep_researcher.supervisory_cli "%topic%" --out /app/output/%output_file% --provider %provider% --model %model% --search-api %search_api% --max-loops %max_loops% --verbose

if %errorlevel% equ 0 (
    call :print_message "研究完成！报告已保存到: output\%output_file%"
) else (
    call :print_error "研究失败"
    exit /b 1
)
exit /b 0

REM 清理资源
:cleanup
call :print_message "清理 Docker 资源..."
docker-compose -f docker-compose-supervisory.yml down
exit /b 0

REM 显示帮助信息
:show_help
echo 主管架构研究系统便捷脚本
echo.
echo 用法:
echo   %~nx0 "研究主题" [输出文件] [LLM提供商] [模型] [搜索引擎] [最大循环次数]
echo.
echo 参数:
echo   研究主题        必需，要研究的主题
echo   输出文件        可选，输出文件名 (默认: supervisory_research_report.md)
echo   LLM提供商       可选，ollama 或 openai (默认: ollama)
echo   模型           可选，模型名称 (默认: llama3)
echo   搜索引擎       可选，duckduckgo/tavily/perplexity/searxng (默认: duckduckgo)
echo   最大循环次数    可选，1-5 (默认: 3)
echo.
echo 示例:
echo   %~nx0 "人工智能发展趋势"
echo   %~nx0 "量子计算应用" ai_report.md ollama llama3 duckduckgo 2
echo.
echo 选项:
echo   -h, --help     显示此帮助信息
echo   --cleanup      清理 Docker 资源
echo   --check        检查服务状态
exit /b 0

REM 检查服务状态
:check_status
call :print_message "检查服务状态..."

call :check_docker
if %errorlevel% neq 0 exit /b 1

call :check_ollama
exit /b 0

REM 主函数
:main
call :print_header

REM 处理命令行参数
if "%1"=="-h" goto :show_help
if "%1"=="--help" goto :show_help
if "%1"=="--cleanup" goto :cleanup
if "%1"=="--check" goto :check_status
if "%1"=="" (
    call :print_error "请提供研究主题"
    goto :show_help
)

REM 检查 Docker
call :check_docker
if %errorlevel% neq 0 exit /b 1

REM 检查并启动 Ollama
call :check_ollama
if %errorlevel% neq 0 (
    call :start_ollama
    if %errorlevel% neq 0 (
        call :print_error "无法启动 Ollama 服务"
        exit /b 1
    )
)

REM 下载模型
call :download_model "%4"
if %errorlevel% neq 0 exit /b 1

REM 运行研究
call :run_supervisory_research %*
if %errorlevel% neq 0 exit /b 1

call :print_message "主管架构研究完成！"
exit /b 0

REM 运行主函数
call :main %*
