import os
from enum import Enum
from pydantic import BaseModel, Field
from typing import Any, Optional, Literal

from langchain_core.runnables import RunnableConfig


class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    SEARXNG = "searxng"


class Configuration(BaseModel):
    """集中管理研究助手的所有可配置项"""

    max_web_research_loops: int = Field(
        default_factory=lambda: int(os.environ.get("MAX_WEB_RESEARCH_LOOPS", "3")),
        title="Research Depth",
        description="Number of research iterations to perform",
    )
    local_llm: str = Field(
        default_factory=lambda: os.environ.get("LOCAL_LLM", "llama3"),
        title="LLM Model Name",
        description="Name of the LLM model to use",
    )
    llm_provider: Literal["ollama", "openai"] = Field(
        default_factory=lambda: os.environ.get("LLM_PROVIDER", "openai"),
        title="LLM Provider",
        description="Provider for the LLM (ollama or openAI)",
    )
    search_api: Literal["perplexity", "tavily", "duckduckgo", "searxng"] = Field(
        default_factory=lambda: os.environ.get("SEARCH_API", "duckduckgo"),
        title="Search API", 
        description="Web search API to use"
    )
    fetch_full_page: bool = Field(
        default_factory=lambda: os.environ.get("FETCH_FULL_PAGE", "true").lower() == "true",
        title="Fetch Full Page",
        description="Include the full page content in the search results",
    )
    ollama_base_url: str = Field(
        default_factory=lambda: os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/"),
        title="Ollama Base URL",
        description="Base URL for Ollama API",
    )
    openai_base_url: str = Field(
        default_factory=lambda: os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        title="OpenAI Base URL",
        description="Base URL for OpenAI-compatible API",
    )
    strip_thinking_tokens: bool = Field(
        default_factory=lambda: os.environ.get("STRIP_THINKING_TOKENS", "true").lower() == "true",
        title="Strip Thinking Tokens",
        description="Whether to strip <think> tokens from model responses",
    )
    use_tool_calling: bool = Field(
        default_factory=lambda: os.environ.get("USE_TOOL_CALLING", "false").lower() == "true",
        title="Use Tool Calling",
        description="Use tool calling instead of JSON mode for structured output",
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
