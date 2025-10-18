# Local Deep Researcher

Local Deep Researcher 是一个完全本地化的网络研究助手，支持使用 [Ollama](https://ollama.com/search) 或 [OpenAI](https://openai.com/) 托管的任何 LLM。给它一个主题，它会生成网络搜索查询、收集搜索结果、总结搜索结果、反思摘要以检查知识缺口、生成新的搜索查询来解决这些缺口，并重复用户定义次数的循环。它将为用户提供包含所有用于生成摘要的来源的最终 Markdown 摘要。

![Langgraph-deep-research](https://github.com/user-attachments/assets/1c6b28f8-6b64-42ba-a491-1ab2875d50ea)




## 🚀 快速开始

克隆仓库：
```shell
git clone https://github.com/langchain-ai/local-deep-researcher.git
cd local-deep-researcher
```

然后根据您的需要编辑 `.env` 文件来自定义环境变量。这些环境变量控制模型选择、搜索工具和其他配置设置。当您运行应用程序时，这些值将通过 `python-dotenv` 自动加载。
```shell
cp .env.example .env
```

### 使用 Ollama 选择本地模型

1. 从 [这里](https://ollama.com/download) 下载 Ollama 应用。

2. 从 [Ollama](https://ollama.com/search) 拉取本地 LLM。以 [DeepSeek R1](https://ollama.com/library/deepseek-r1:8b) 为例：
```shell
ollama pull deepseek-r1:8b
```

3. 可选地，使用以下 Ollama 配置设置更新 `.env` 文件。

* 如果设置了这些值，它们将优先于 `configuration.py` 中 `Configuration` 类设置的默认值。
```shell
LLM_PROVIDER=ollama
OLLAMA_BASE_URL="http://localhost:11434" # Ollama 服务端点，默认为 `http://localhost:11434`
LOCAL_LLM=model # 要使用的模型，如果未设置则默认为 `llama3`
```

### 选择搜索工具

默认情况下，它将使用 [DuckDuckGo](https://duckduckgo.com/) 进行网络搜索，无需 API 密钥。但您也可以通过将 API 密钥添加到环境文件中来使用 [SearXNG](https://docs.searxng.org/)、[Tavily](https://tavily.com/) 或 [Perplexity](https://www.perplexity.ai/hub/blog/introducing-the-sonar-pro-api)。可选地，使用以下搜索工具配置和 API 密钥更新 `.env` 文件。如果设置了这些值，它们将优先于 `configuration.py` 中 `Configuration` 类设置的默认值。
```shell
SEARCH_API=xxx # 要使用的搜索 API，如 `duckduckgo`（默认）
TAVILY_API_KEY=xxx # 要使用的 tavily API 密钥
PERPLEXITY_API_KEY=xxx # 要使用的 perplexity API 密钥
MAX_WEB_RESEARCH_LOOPS=xxx # 研究循环步骤的最大数量，默认为 `3`
FETCH_FULL_PAGE=xxx # 获取完整页面内容（使用 `duckduckgo` 时），默认为 `true`
USE_TOOL_CALLING=xxx # 使用工具调用而不是 JSON 模式，默认为 `false`
STRIP_THINKING_TOKENS=xxx # 从模型响应中去除 <think> 令牌，默认为 `true`
```

### 从终端运行

#### Mac/Linux

1. （推荐）创建虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate
```

2. 安装依赖并运行：

```bash
# 安装依赖
pip install -e .

# 运行研究助手
python -m Langgraph_deep_researcher --topic "您的研究主题" --out research_report.md
```

#### Windows

1. （推荐）创建虚拟环境：

* 安装 `Python 3.11`（并在安装过程中添加到 PATH）。
* 重启终端以确保 Python 可用，然后创建并激活虚拟环境：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. 安装依赖并运行：

```powershell
# 安装依赖
pip install -e .

# 运行研究助手
python -m Langgraph_deep_researcher --topic "您的研究主题" --out research_report.md
```

### 命令行使用

您也可以使用命令行参数来自定义研究：

```bash
python -m Langgraph_deep_researcher --topic "人工智能趋势" --out ai_trends.md --provider ollama --model llama3 --loops 5
```

可用选项：
- `--topic`: 研究主题（必需）
- `--out`: 输出文件路径（必需）
- `--provider`: 在 "ollama" 或 "openai" 之间选择
- `--model`: 指定模型名称（如 "llama3", "gpt-4"）
- `--loops`: 研究迭代次数（默认：3）
- `--search`: 要使用的搜索 API（"duckduckgo", "tavily", "perplexity", "searxng"）
- `--tool-calling`: 使用工具调用而不是 JSON 模式
- `--no-strip-think`: 不从模型响应中去除 <think> 令牌

### 模型兼容性说明

选择本地 LLM 时，某些步骤使用结构化 JSON 输出。一些模型可能难以满足此要求，助手具有回退机制来处理这种情况。例如，[DeepSeek R1 (7B)](https://ollama.com/library/deepseek-llm:7b) 和 [DeepSeek R1 (1.5B)](https://ollama.com/library/deepseek-r1:1.5b) 模型难以生成所需的 JSON 输出，助手将使用回退机制来处理这种情况。

对于这些模型，建议使用 `--tool-calling` 选项来启用工具调用模式，这通常比 JSON 模式更可靠。
  

## 工作原理

Local Deep Researcher 受到 [IterDRAG](https://arxiv.org/html/2410.04343v1#:~:text=To%20tackle%20this%20issue%2C%20we,used%20to%20generate%20intermediate%20answers.) 的启发。这种方法将查询分解为子查询，为每个子查询检索文档，回答子查询，然后通过为第二个子查询检索文档来构建答案。在这里，我们做类似的事情：

1. **生成搜索查询** - 给定用户提供的主题，使用本地 LLM（通过 [Ollama](https://ollama.com/search) 或 [OpenAI](https://openai.com/)）生成网络搜索查询
2. **执行网络搜索** - 使用搜索引擎/工具找到相关来源
3. **总结发现** - 使用 LLM 总结与用户提供的研究主题相关的网络搜索结果
4. **反思摘要** - 然后使用 LLM 反思摘要，识别知识缺口
5. **生成后续查询** - 生成新的搜索查询来解决知识缺口
6. **迭代更新** - 过程重复，摘要通过来自网络搜索的新信息进行迭代更新
7. **可配置循环** - 运行可配置次数的迭代（参见配置部分）

## 输出结果

研究助手生成包含以下内容的综合 Markdown 报告：

- **研究摘要**：对您主题的详细分析
- **信息来源**：研究中使用的所有网络来源，带有适当的引用
- **研究过程**：有关使用的迭代研究方法的信息

最终报告保存为 Markdown 文件，您可以查看、共享或进一步处理。


## 作为 Docker 容器运行

包含的 `Dockerfile` 将研究助手作为命令行工具运行。您必须单独运行 Ollama 并配置 `OLLAMA_BASE_URL` 环境变量。您也可以通过提供 `LOCAL_LLM` 环境变量来指定要使用的 Ollama 模型。

### 基础 Docker 使用

克隆仓库并构建镜像：
```bash
$ docker build -t local-deep-researcher .
```

使用研究主题运行容器：
```bash
$ docker run --rm -it \
  -e LLM_PROVIDER=ollama \
  -e OLLAMA_BASE_URL="http://host.docker.internal:11434/" \
  -e LOCAL_LLM="llama3" \
  -v $(pwd)/output:/app/output \
  local-deep-researcher \
  --topic "您的研究主题" \
  --out "/app/output/research_report.md"
```

### 使用 Docker Compose（推荐）

项目包含 `docker-compose.yml` 文件，简化了 Docker 的使用：

```bash
# 基础使用
$ docker-compose run --rm deep-researcher

# 自定义研究主题
$ RESEARCH_TOPIC="量子计算最新进展" docker-compose run --rm deep-researcher

# 自定义输出文件
$ RESEARCH_TOPIC="区块链技术" OUTPUT_FILE="blockchain_research.md" docker-compose run --rm deep-researcher

# 使用 OpenAI
$ LLM_PROVIDER=openai OPENAI_API_KEY=your_key RESEARCH_TOPIC="AI trends" docker-compose run --rm deep-researcher

# 使用 Tavily 搜索
$ SEARCH_API=tavily TAVILY_API_KEY=your_key RESEARCH_TOPIC="Machine learning" docker-compose run --rm deep-researcher
```

### Docker 环境变量

Docker 容器支持以下环境变量配置：

```bash
# LLM 配置
LLM_PROVIDER=ollama                    # 或 openai
LOCAL_LLM=llama3                       # 模型名称
OLLAMA_BASE_URL=http://host.docker.internal:11434/ # Ollama 服务地址
OPENAI_API_KEY=your_openai_api_key     # OpenAI API 密钥

# 搜索配置
SEARCH_API=duckduckgo                  # 搜索引擎选择
TAVILY_API_KEY=your_tavily_key         # Tavily API 密钥
PERPLEXITY_API_KEY=your_perplexity_key # Perplexity API 密钥

# 研究配置
MAX_WEB_RESEARCH_LOOPS=3               # 研究循环次数
RESEARCH_TOPIC=人工智能发展趋势         # 默认研究主题
OUTPUT_FILE=research_report.md         # 默认输出文件名

# 高级选项
USE_TOOL_CALLING=false                 # 使用工具调用模式
STRIP_THINKING_TOKENS=true             # 去除思维令牌
```

## 🔧 高级配置

### 环境变量

项目支持以下环境变量进行配置：

```shell
# LLM 配置
LLM_PROVIDER=ollama                    # 或 openai
LOCAL_LLM=llama3                       # 模型名称
OLLAMA_BASE_URL=http://localhost:11434 # Ollama 服务地址
OPENAI_BASE_URL=https://api.openai.com/v1 # OpenAI API 地址

# 搜索配置
SEARCH_API=duckduckgo                  # 搜索引擎选择
TAVILY_API_KEY=your_tavily_key         # Tavily API 密钥
PERPLEXITY_API_KEY=your_perplexity_key # Perplexity API 密钥
SEARXNG_URL=http://localhost:8888      # SearXNG 服务地址

# 研究配置
MAX_WEB_RESEARCH_LOOPS=3               # 最大研究循环次数
FETCH_FULL_PAGE=true                   # 是否获取完整页面内容

# 高级选项
USE_TOOL_CALLING=false                 # 使用工具调用模式
STRIP_THINKING_TOKENS=true             # 去除思维令牌
```

### 支持的模型

**Ollama 模型：**
- llama3, llama3.2
- deepseek-r1:8b, deepseek-r1:1.5b
- qwen2.5, codellama
- 其他兼容 Ollama 的模型

**OpenAI 兼容模型：**
- gpt-4, gpt-3.5-turbo
- 任何 OpenAI 兼容 API 的模型

## 📊 使用示例

### 基础使用
```bash
# 使用默认设置研究人工智能趋势
python -m Langgraph_deep_researcher --topic "人工智能发展趋势" --out ai_trends.md
```

### 高级使用
```bash
# 使用 Ollama + DeepSeek R1 进行深度研究
python -m Langgraph_deep_researcher \
  --topic "量子计算最新进展" \
  --out quantum_computing.md \
  --provider ollama \
  --model deepseek-r1:8b \
  --loops 5 \
  --search tavily \
  --tool-calling
```

### Docker 使用
```bash
# 构建并运行 Docker 容器
docker build -t local-deep-researcher .
docker run --rm -v $(pwd):/app/output \
  -e LLM_PROVIDER=ollama \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  -e LOCAL_LLM=llama3 \
  local-deep-researcher \
  --topic "区块链技术应用" \
  --out /app/output/blockchain_research.md
```

### 使用便捷脚本

项目包含便捷脚本简化 Docker 使用：

**Linux/macOS:**
```bash
# 基础使用
./docker-run.sh "您的研究主题"

# 自定义输出文件
./docker-run.sh "量子计算" quantum_research.md

# 使用环境变量
RESEARCH_TOPIC="AI趋势" LLM_PROVIDER=openai ./docker-run.sh
```

**Windows:**
```cmd
REM 基础使用
docker-run.bat "您的研究主题"

REM 自定义输出文件
docker-run.bat "量子计算" quantum_research.md

REM 使用环境变量
set RESEARCH_TOPIC=AI趋势
set LLM_PROVIDER=openai
docker-run.bat
```

## 🚨 故障排除

### 常见问题

1. **模型无法生成 JSON 输出**
   - 解决方案：使用 `--tool-calling` 选项
   - 原因：某些模型（如 DeepSeek R1）在 JSON 模式下表现不佳

2. **搜索 API 密钥错误**
   - 检查环境变量是否正确设置
   - 确认 API 密钥有效且有足够配额

3. **Ollama 连接失败**
   - 确认 Ollama 服务正在运行
   - 检查 `OLLAMA_BASE_URL` 是否正确

4. **内存不足**
   - 减少 `MAX_WEB_RESEARCH_LOOPS` 值
   - 使用较小的模型
   - 禁用 `FETCH_FULL_PAGE` 选项

### 调试模式

启用详细日志输出：
```bash
python -m Langgraph_deep_researcher --topic "测试主题" --out test.md --loops 1
```

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 此仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目基于 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain) - LLM 应用框架
- [LangGraph](https://github.com/langchain-ai/langgraph) - 状态图构建工具
- [Ollama](https://ollama.com/) - 本地 LLM 部署
- [IterDRAG](https://arxiv.org/html/2410.04343v1) - 研究灵感来源

