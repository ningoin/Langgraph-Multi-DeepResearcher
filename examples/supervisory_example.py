"""
主管架构系统使用示例
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from Langgraph_deep_researcher.supervisory_architecture import (
    supervisory_graph,
    run_supervisory_research,
    SupervisoryStateInput
)
from Langgraph_deep_researcher.configuration import Configuration


async def example_usage():
    """使用示例"""
    print("🚀 主管架构系统示例")
    print("=" * 50)
    
    # 配置
    config = Configuration(
        llm_provider="ollama",
        local_llm="llama3",
        search_api="duckduckgo",
        max_web_research_loops=2
    )
    
    # 用户请求
    user_request = "请研究人工智能在医疗领域的最新应用，分析其发展趋势和挑战"
    
    print(f"📝 用户请求: {user_request}")
    print("\n🔄 开始执行主管架构流程...")
    
    try:
        # 运行主管架构研究
        result = await run_supervisory_research(user_request, config)
        
        print("\n✅ 研究完成!")
        print("\n📊 研究结果:")
        for i, research_result in enumerate(result.research_results, 1):
            print(f"\n--- 研究结果 {i} ---")
            print(research_result[:200] + "..." if len(research_result) > 200 else research_result)
        
        print("\n🔍 分析结果:")
        for i, analysis_result in enumerate(result.analysis_results, 1):
            print(f"\n--- 分析结果 {i} ---")
            print(analysis_result[:200] + "..." if len(analysis_result) > 200 else analysis_result)
        
        print("\n📄 最终综合报告:")
        print("=" * 50)
        print(result.final_synthesis)
        
        # 保存结果到文件
        output_file = "supervisory_research_report.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# 主管架构研究报告\n\n")
            f.write(f"**用户请求**: {user_request}\n\n")
            
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
        
        print(f"\n💾 报告已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 执行失败: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        user_request = " ".join(sys.argv[1:])
    else:
        user_request = input("请输入您的研究请求: ")
    
    print(f"🎯 开始处理请求: {user_request}")
    
    # 运行异步示例
    asyncio.run(example_usage())


if __name__ == "__main__":
    main()
