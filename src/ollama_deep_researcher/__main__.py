import argparse
import os
import sys
from pathlib import Path

try:
    # Prefer python-dotenv if available to load .env before reading os.environ
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

from langgraph.checkpoint.memory import MemorySaver

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ollama_deep_researcher.graph import graph
from ollama_deep_researcher.state import SummaryStateInput
from ollama_deep_researcher.configuration import Configuration


def main():
    # Load environment variables from nearest .env if python-dotenv is available
    # This allows LOCAL_LLM、LLM_PROVIDER 等在 CLI 模式下生效
    if load_dotenv is not None:
        # Search from CWD upwards to project root for a .env
        # This mimics common tooling behavior and is harmless if not found
        cwd = Path.cwd()
        env_path = None
        for parent in [cwd, *cwd.parents]:
            candidate = parent / ".env"
            if candidate.exists():
                env_path = candidate
                break
        if env_path is not None:
            load_dotenv(dotenv_path=str(env_path), override=False)
    parser = argparse.ArgumentParser(
        prog="ollama_deep_researcher",
        description="Run local deep researcher from CLI and write output to a file.",
    )
    parser.add_argument(
        "--topic",
        required=True,
        help="Research topic to investigate",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Output file path for the final markdown summary",
    )
    parser.add_argument(
        "--loops",
        type=int,
        default=None,
        help="Override max research loops (optional)",
    )
    parser.add_argument(
        "--provider",
        choices=["ollama", "lmstudio", "openai"],
        default=None,
        help="Override LLM provider (optional)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override local model name (optional)",
    )
    parser.add_argument(
        "--search",
        choices=["duckduckgo", "tavily", "perplexity", "searxng"],
        default=None,
        help="Override search API (optional)",
    )
    parser.add_argument(
        "--tool-calling",
        action="store_true",
        default=None,
        help="Use tool calling instead of JSON mode",
    )
    parser.add_argument(
        "--no-strip-think",
        action="store_true",
        default=None,
        help="Do not strip <think> tokens from model responses",
    )

    args = parser.parse_args()

    # Prepare configurable overrides. Only include keys explicitly set.
    configurable_overrides = {}
    if args.loops is not None:
        configurable_overrides["max_web_research_loops"] = args.loops
    if args.provider is not None:
        configurable_overrides["llm_provider"] = args.provider
    if args.model is not None:
        configurable_overrides["local_llm"] = args.model
    if args.search is not None:
        configurable_overrides["search_api"] = args.search
    if args.tool_calling is not None:
        configurable_overrides["use_tool_calling"] = True
    if args.no_strip_think is not None:
        configurable_overrides["strip_thinking_tokens"] = False

    # Build RunnableConfig expected by the graph
    runnable_config = {"configurable": configurable_overrides} if configurable_overrides else {}

    # Optional in-memory checkpointer; not required but helpful for consistency
    # Note: graph compiled in module already; we can use .invoke

    # Run the graph synchronously
    input_state = SummaryStateInput(research_topic=args.topic)
    result = graph.invoke(input_state, config=runnable_config)

    summary = result.get("running_summary")
    if not summary:
        print("Error: No running_summary produced by graph.", file=sys.stderr)
        sys.exit(1)

    # Ensure directory exists
    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"✅ Summary written to: {out_path}")


if __name__ == "__main__":
    main()


