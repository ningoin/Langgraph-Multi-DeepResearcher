import argparse
import os
import sys
import time
from pathlib import Path

try:
    # Prefer python-dotenv if available to load .env before reading os.environ
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

from langgraph.checkpoint.memory import MemorySaver

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Langgraph_deep_researcher.graph import graph
from Langgraph_deep_researcher.state import SummaryStateInput
from Langgraph_deep_researcher.configuration import Configuration


def print_progress(message: str, step: int = None, total: int = None):
    """打印进度信息"""
    timestamp = time.strftime("%H:%M:%S")
    if step and total:
        print(f"[{timestamp}] 步骤 {step}/{total}: {message}")
    else:
        print(f"[{timestamp}] {message}")


def print_step_complete(step_name: str, duration: float):
    """打印步骤完成信息"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] ✅ {step_name} 完成 (耗时: {duration:.1f}秒)")


def print_research_progress(state, step_name: str):
    """打印研究进度信息"""
    timestamp = time.strftime("%H:%M:%S")
    
    # 处理状态可能是字典或对象的情况
    if isinstance(state, dict):
        loop_count = state.get('research_loop_count', 0)
        sources_gathered = state.get('sources_gathered', [])
        running_summary = state.get('running_summary', '')
    else:
        loop_count = getattr(state, 'research_loop_count', 0)
        sources_gathered = getattr(state, 'sources_gathered', [])
        running_summary = getattr(state, 'running_summary', '')
    
    sources_count = len(sources_gathered) if sources_gathered else 0
    summary_length = len(running_summary) if running_summary else 0
    
    print(f"[{timestamp}] 🔍 {step_name}")
    print(f"    📊 研究循环: {loop_count}, 来源数量: {sources_count}, 摘要长度: {summary_length} 字符")


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
        prog="Langgraph_deep_researcher",
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
        choices=["ollama", "openai"],
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

    # 显示开始信息
    print_progress(f"🚀 开始研究主题: {args.topic}")
    print_progress(f"📁 输出文件: {args.out}")
    if configurable_overrides:
        print_progress(f"⚙️ 配置覆盖: {configurable_overrides}")
    
    start_time = time.time()
    
    # Run the graph with streaming to show progress
    input_state = SummaryStateInput(research_topic=args.topic)
    
    # 使用流式执行来显示进度
    print_progress("🔄 正在执行研究流程...")
    
    # 跟踪步骤
    step_count = 0
    total_steps = 5  # generate_query, web_research, summarize_sources, reflect_on_summary, finalize_summary
    
    try:
        # 使用 stream 方法来获取实时进度
        for chunk in graph.stream(input_state, config=runnable_config):
            step_count += 1
            node_name = list(chunk.keys())[0] if chunk else "unknown"
            state = list(chunk.values())[0] if chunk else None
            
            # 调试信息：显示状态类型和内容
            if state:
                print_progress(f"🔍 调试: 节点={node_name}, 状态类型={type(state)}")
                if isinstance(state, dict):
                    print_progress(f"    📋 状态字段: {list(state.keys())}")
                else:
                    print_progress(f"    📋 状态属性: {dir(state)[:5]}...")
            
            # 根据节点名称显示不同的进度信息
            if node_name == "generate_query":
                print_progress("📝 生成搜索查询", step_count, total_steps)
            elif node_name == "web_research":
                print_research_progress(state, "🌐 执行网络搜索")
            elif node_name == "summarize_sources":
                print_research_progress(state, "📋 总结信息来源")
            elif node_name == "reflect_on_summary":
                print_research_progress(state, "🤔 反思研究进度")
            elif node_name == "finalize_summary":
                print_progress("📄 生成最终报告", step_count, total_steps)
            
            # 短暂延迟以便用户看到进度
            time.sleep(0.1)
        
        # 获取最终结果
        result = graph.invoke(input_state, config=runnable_config)
        
    except Exception as e:
        print_progress(f"❌ 执行过程中出现错误: {str(e)}")
        sys.exit(1)

    summary = result.get("running_summary")
    if not summary:
        print_progress("❌ 错误: 图执行未产生运行摘要")
        sys.exit(1)

    # 显示完成信息
    total_time = time.time() - start_time
    print_step_complete("研究流程", total_time)
    
    # Ensure directory exists
    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # 写入文件
    print_progress(f"💾 正在写入文件: {out_path}")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(summary)

    # 显示最终统计信息
    summary_length = len(summary) if summary else 0
    sources_gathered = result.get("sources_gathered", [])
    sources_count = len(sources_gathered) if sources_gathered else 0
    print_progress(f"📊 研究完成统计:")
    print_progress(f"   📄 报告长度: {summary_length:,} 字符")
    print_progress(f"   🔗 信息来源: {sources_count} 个")
    print_progress(f"   ⏱️ 总耗时: {total_time:.1f} 秒")
    print(f"✅ 研究摘要已保存至: {out_path}")


if __name__ == "__main__":
    main()


