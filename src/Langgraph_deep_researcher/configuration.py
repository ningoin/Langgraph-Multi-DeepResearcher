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
        default=3,
        title="Research Depth",
        description="Number of research iterations to perform",
    )
    local_llm: str = Field(
        default="llama3",
        title="LLM Model Name",
        description="Name of the LLM model to use",
    )
    llm_provider: Literal["ollama", "openai"] = Field(
        default="openai",
        title="LLM Provider",
        description="Provider for the LLM (ollama or openAI)",
    )
    search_api: Literal["perplexity", "tavily", "duckduckgo", "searxng"] = Field(
        default="duckduckgo", title="Search API", description="Web search API to use"
    )
    fetch_full_page: bool = Field(
        default=True,
        title="Fetch Full Page",
        description="Include the full page content in the search results",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434/",
        title="Ollama Base URL",
        description="Base URL for Ollama API",
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        title="OpenAI Base URL",
        description="Base URL for OpenAI-compatible API",
    )
    strip_thinking_tokens: bool = Field(
        default=True,
        title="Strip Thinking Tokens",
        description="Whether to strip <think> tokens from model responses",
    )
    use_tool_calling: bool = Field(
        default=False,
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
