"""
主管架构系统命令行接口
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

try:
    # Prefer python-dotenv if available to load .env before reading os.environ
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from Langgraph_deep_researcher.supervisory_architecture import (
    supervisory_graph,
    run_supervisory_research
)
from Langgraph_deep_researcher.configuration import Configuration, SearchAPI


def create_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="主管架构研究系统 - 多 Agent 协作研究",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m Langgraph_deep_researcher.supervisory_cli "人工智能发展趋势"
  python -m Langgraph_deep_researcher.supervisory_cli --topic "量子计算应用" --out report.md
  python -m Langgraph_deep_researcher.supervisory_cli --provider openai --model gpt-4 "医疗AI研究"
        """
    )
    
    # 必需参数
    parser.add_argument(
        "topic",
        nargs="?",
        help="研究主题"
    )
    
    # 可选参数
    parser.add_argument(
        "--topic", "-t",
        dest="research_topic",
        help="研究主题 (与位置参数相同)"
    )
    
    parser.add_argument(
        "--out", "-o",
        help="输出文件路径 (默认: supervisory_research_report.md)"
    )
    
    parser.add_argument(
        "--provider",
        choices=["ollama", "openai"],
        default="ollama",
        help="LLM 提供商 (默认: ollama)"
    )
    
    parser.add_argument(
        "--model",
        default="llama3",
        help="LLM 模型名称 (默认: llama3)"
    )
    
    parser.add_argument(
        "--search-api",
        choices=["duckduckgo", "tavily", "perplexity", "searxng"],
        default="duckduckgo",
        help="搜索引擎 API (默认: duckduckgo)"
    )
    
    parser.add_argument(
        "--max-loops",
        type=int,
        default=3,
        help="最大研究循环次数 (默认: 3)"
    )
    
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama 服务地址 (默认: http://localhost:11434)"
    )
    
    parser.add_argument(
        "--openai-url",
        default="https://api.openai.com/v1",
        help="OpenAI API 地址 (默认: https://api.openai.com/v1)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    
    return parser


def print_progress(message: str, verbose: bool = False):
    """打印进度信息"""
    # 在verbose模式下显示详细信息，否则只显示关键进度
    if verbose or "开始执行" in message or "研究完成" in message or "报告已保存" in message:
        print(f"🔄 {message}")


async def run_supervisory_research_cli(args):
    """运行主管架构研究"""
    # 确定研究主题
    topic = args.topic or args.research_topic
    if not topic:
        print("❌ 错误: 请提供研究主题")
        return False
    
    # 创建配置 - 优先级: .env文件 > 命令行参数 > 默认值
    # 从环境变量获取默认值（.env文件已加载）
    default_config = Configuration.from_runnable_config()
    
    # 准备配置覆盖参数 - 只有明确指定的命令行参数才覆盖
    config_overrides = {}
    
    # 检查是否使用了默认值，如果是则使用环境变量中的值
    if args.provider == "ollama" and hasattr(default_config, 'llm_provider') and default_config.llm_provider != "ollama":
        # 使用环境变量中的值
        pass  # 不覆盖，使用环境变量
    elif args.provider != "ollama":
        # 用户明确指定了非默认值
        config_overrides["llm_provider"] = args.provider
    
    if args.model == "llama3" and hasattr(default_config, 'local_llm') and default_config.local_llm != "llama3":
        # 使用环境变量中的值
        pass  # 不覆盖，使用环境变量
    elif args.model != "llama3":
        # 用户明确指定了非默认值
        config_overrides["local_llm"] = args.model
    
    if args.search_api == "duckduckgo" and hasattr(default_config, 'search_api') and default_config.search_api != "duckduckgo":
        # 使用环境变量中的值
        pass  # 不覆盖，使用环境变量
    elif args.search_api != "duckduckgo":
        # 用户明确指定了非默认值
        config_overrides["search_api"] = args.search_api
    
    if args.max_loops == 3 and hasattr(default_config, 'max_web_research_loops') and default_config.max_web_research_loops != 3:
        # 使用环境变量中的值
        pass  # 不覆盖，使用环境变量
    elif args.max_loops != 3:
        # 用户明确指定了非默认值
        config_overrides["max_web_research_loops"] = args.max_loops
    
    if args.ollama_url == "http://localhost:11434" and hasattr(default_config, 'ollama_base_url') and default_config.ollama_base_url != "http://localhost:11434":
        # 使用环境变量中的值
        pass  # 不覆盖，使用环境变量
    elif args.ollama_url != "http://localhost:11434":
        # 用户明确指定了非默认值
        config_overrides["ollama_base_url"] = args.ollama_url
    
    if args.openai_url == "https://api.openai.com/v1" and hasattr(default_config, 'openai_base_url') and default_config.openai_base_url != "https://api.openai.com/v1":
        # 使用环境变量中的值
        pass  # 不覆盖，使用环境变量
    elif args.openai_url != "https://api.openai.com/v1":
        # 用户明确指定了非默认值
        config_overrides["openai_base_url"] = args.openai_url
    
    # 创建最终配置
    config = Configuration(**{**default_config.model_dump(), **config_overrides})
    
    print(f"🎯 研究主题: {topic}")
    print(f"🤖 LLM 提供商: {config.llm_provider}")
    print(f"🧠 模型: {config.local_llm}")
    print(f"🔍 搜索引擎: {config.search_api}")
    print(f"🔄 最大循环次数: {config.max_web_research_loops}")
    print("=" * 50)
    
    try:
        print_progress("开始执行主管架构研究流程...", args.verbose)
        
        # 运行研究
        result = await run_supervisory_research(topic, config, verbose=args.verbose)
        
        print("✅ 研究完成!")
        
        # 确定输出文件
        output_file = args.out or "supervisory_research_report.md"
        
        # 保存结果
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# 主管架构研究报告\n\n")
            f.write(f"**研究主题**: {topic}\n\n")
            f.write(f"**LLM 提供商**: {config.llm_provider}\n")
            f.write(f"**模型**: {config.local_llm}\n")
            f.write(f"**搜索引擎**: {config.search_api}\n")
            f.write(f"**最大循环次数**: {config.max_web_research_loops}\n\n")
            
            f.write("## 研究结果\n\n")
            for i, research_result in enumerate(result.research_results, 1):
                f.write(f"### 研究结果 {i}\n\n")
                f.write(research_result)
                f.write("\n\n")
            
            f.write("## 分析结果\n\n")
            for i, analysis_result in enumerate(result.analysis_results, 1):
                f.write(f"### 分析结果 {i}\n\n")
                f.write(analysis_result)
                f.write("\n\n")
            
            f.write("## 最终综合报告\n\n")
            f.write(result.final_synthesis)
        
        print(f"💾 报告已保存到: {output_file}")
        
        # 显示摘要
        if args.verbose:
            print("\n📊 研究摘要:")
            print(f"- 研究结果数量: {len(result.research_results)}")
            print(f"- 分析结果数量: {len(result.analysis_results)}")
            print(f"- 最终报告长度: {len(result.final_synthesis)} 字符")
        
        return True
        
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    """主函数"""
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
            print(f"📁 已加载环境变量文件: {env_path}")
    
    parser = create_parser()
    args = parser.parse_args()
    
    # 运行异步研究
    success = asyncio.run(run_supervisory_research_cli(args))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
