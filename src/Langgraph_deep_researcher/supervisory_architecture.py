"""
主管架构系统 - Supervisory Architecture
将 Deep Researcher 作为子 agent，由主管智能体协调管理
"""

import asyncio
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

from Langgraph_deep_researcher.graph import graph as deep_researcher_graph
from Langgraph_deep_researcher.state import SummaryStateInput
from Langgraph_deep_researcher.configuration import Configuration


class TaskType(Enum):
    """任务类型枚举"""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"


class AgentStatus(Enum):
    """Agent 状态枚举"""
    IDLE = "idle"
    BUSY = "busy"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class Task:
    """任务数据结构"""
    id: str
    type: TaskType
    description: str
    priority: int = 1  # 1-5, 5为最高优先级
    assigned_agent: Optional[str] = None
    status: str = "pending"
    result: Optional[str] = None
    metadata: Dict[str, Any] = None


class SupervisoryState(BaseModel):
    """主管智能体状态"""
    # 用户输入
    user_request: str = Field(description="用户的原始请求")
    
    # 任务管理
    tasks: List[Task] = Field(default_factory=list, description="任务列表")
    current_task_index: int = Field(default=0, description="当前任务索引")
    
    # Agent 状态
    deep_researcher_status: AgentStatus = Field(default=AgentStatus.IDLE)
    analysis_agent_status: AgentStatus = Field(default=AgentStatus.IDLE)
    
    # 结果存储
    research_results: List[str] = Field(default_factory=list)
    analysis_results: List[str] = Field(default_factory=list)
    final_synthesis: str = Field(default="")
    
    # 对话历史
    messages: List[BaseMessage] = Field(default_factory=list)
    
    # 配置
    config: Dict[str, Any] = Field(default_factory=dict)


class SupervisoryStateInput(BaseModel):
    """主管智能体输入"""
    user_request: str


class SupervisoryStateOutput(BaseModel):
    """主管智能体输出"""
    final_synthesis: str
    research_results: List[str]
    analysis_results: List[str]


class SupervisoryAgent:
    """主管智能体 - 负责任务分解、分配和协调"""
    
    def __init__(self, config: Configuration, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.llm = self._get_llm()
        
    def _print_progress(self, message: str, level: str = "INFO"):
        """打印进度信息"""
        if self.verbose:
            icons = {
                "INFO": "ℹ️",
                "SUCCESS": "✅", 
                "WARNING": "⚠️",
                "ERROR": "❌",
                "PROGRESS": "🔄",
                "TASK": "📋",
                "RESEARCH": "🔍",
                "ANALYSIS": "🧠",
                "SYNTHESIS": "📝"
            }
            icon = icons.get(level, "ℹ️")
            print(f"{icon} {message}")
        
    def _get_llm(self):
        """获取 LLM 实例"""
        if self.config.llm_provider == "openai":
            return ChatOpenAI(
                model=self.config.local_llm,
                base_url=self.config.openai_base_url,
                temperature=0.1
            )
        else:
            return ChatOllama(
                model=self.config.local_llm,
                base_url=self.config.ollama_base_url,
                temperature=0.1
            )
    
    def decompose_request(self, user_request: str) -> List[Task]:
        """将用户请求分解为具体任务"""
        self._print_progress(f"开始分解用户请求: {user_request}", "TASK")
        
        decomposition_prompt = f"""
你是一个智能任务分解专家。请将用户的复杂请求分解为具体的、可执行的任务。

用户请求: {user_request}

请按照以下格式输出任务列表（JSON格式）:
{{
    "tasks": [
        {{
            "id": "task_1",
            "type": "research",
            "description": "研究任务描述",
            "priority": 5
        }},
        {{
            "id": "task_2", 
            "type": "analysis",
            "description": "分析任务描述",
            "priority": 4
        }}
    ]
}}

任务类型说明:
- research: 需要深度研究收集信息的任务
- analysis: 需要分析、比较、评估的任务
- synthesis: 需要综合整理的任务
- validation: 需要验证、检查的任务

请确保任务分解合理、具体、可执行。
"""

        messages = [
            SystemMessage(content=decomposition_prompt),
            HumanMessage(content=f"请分解这个请求: {user_request}")
        ]
        
        try:
            self._print_progress("正在调用LLM进行任务分解...", "PROGRESS")
            response = self.llm.invoke(messages)
            self._print_progress("正在解析任务分解结果...", "PROGRESS")
            
            # 这里需要解析 JSON 响应并创建 Task 对象
            # 简化实现，直接创建示例任务
            tasks = [
                Task(
                    id="research_task",
                    type=TaskType.RESEARCH,
                    description=f"深度研究: {user_request}",
                    priority=5
                ),
                Task(
                    id="analysis_task",
                    type=TaskType.ANALYSIS,
                    description=f"分析研究结果并生成见解",
                    priority=4
                ),
                Task(
                    id="synthesis_task",
                    type=TaskType.SYNTHESIS,
                    description="综合所有信息生成最终报告",
                    priority=3
                )
            ]
            
            self._print_progress(f"成功分解为 {len(tasks)} 个任务", "SUCCESS")
            for i, task in enumerate(tasks, 1):
                self._print_progress(f"  任务 {i}: {task.type.value} - {task.description[:50]}...", "INFO")
            
            return tasks
        except Exception as e:
            self._print_progress(f"任务分解失败: {e}", "ERROR")
            self._print_progress("使用默认任务分解策略", "WARNING")
            # 返回默认任务
            return [
                Task(
                    id="research_task",
                    type=TaskType.RESEARCH,
                    description=f"研究: {user_request}",
                    priority=5
                )
            ]


class DeepResearcherAgent:
    """Deep Researcher 子 Agent"""
    
    def __init__(self, config: Configuration, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.status = AgentStatus.IDLE
        
    def _print_progress(self, message: str, level: str = "INFO"):
        """打印进度信息"""
        if self.verbose:
            icons = {
                "INFO": "ℹ️",
                "SUCCESS": "✅", 
                "WARNING": "⚠️",
                "ERROR": "❌",
                "PROGRESS": "🔄",
                "TASK": "📋",
                "RESEARCH": "🔍",
                "ANALYSIS": "🧠",
                "SYNTHESIS": "📝"
            }
            icon = icons.get(level, "ℹ️")
            print(f"{icon} [DeepResearcher] {message}")
    
    async def execute_research(self, task: Task) -> str:
        """执行研究任务"""
        self.status = AgentStatus.BUSY
        self._print_progress(f"开始执行研究任务: {task.description}", "RESEARCH")
        
        try:
            self._print_progress("正在初始化Deep Researcher...", "PROGRESS")
            # 使用现有的 Deep Researcher
            input_state = SummaryStateInput(research_topic=task.description)
            config_dict = {
                "configurable": {
                    "max_web_research_loops": self.config.max_web_research_loops,
                    "llm_provider": self.config.llm_provider,
                    "local_llm": self.config.local_llm,
                    "search_api": self.config.search_api
                }
            }
            
            self._print_progress("正在运行Deep Researcher研究流程...", "PROGRESS")
            result = deep_researcher_graph.invoke(input_state, config=config_dict)
            research_result = result.get("running_summary", "研究失败")
            
            self._print_progress("研究任务完成", "SUCCESS")
            self.status = AgentStatus.COMPLETED
            return research_result
            
        except Exception as e:
            self._print_progress(f"研究任务失败: {e}", "ERROR")
            self.status = AgentStatus.ERROR
            return f"研究执行失败: {str(e)}"


class AnalysisAgent:
    """分析 Agent - 负责分析研究结果"""
    
    def __init__(self, config: Configuration, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.status = AgentStatus.IDLE
        self.llm = self._get_llm()
        
    def _print_progress(self, message: str, level: str = "INFO"):
        """打印进度信息"""
        if self.verbose:
            icons = {
                "INFO": "ℹ️",
                "SUCCESS": "✅", 
                "WARNING": "⚠️",
                "ERROR": "❌",
                "PROGRESS": "🔄",
                "TASK": "📋",
                "RESEARCH": "🔍",
                "ANALYSIS": "🧠",
                "SYNTHESIS": "📝"
            }
            icon = icons.get(level, "ℹ️")
            print(f"{icon} [AnalysisAgent] {message}")
    
    def _get_llm(self):
        """获取 LLM 实例"""
        if self.config.llm_provider == "openai":
            return ChatOpenAI(
                model=self.config.local_llm,
                base_url=self.config.openai_base_url,
                temperature=0.2
            )
        else:
            return ChatOllama(
                model=self.config.local_llm,
                base_url=self.config.ollama_base_url,
                temperature=0.2
            )
    
    async def analyze_results(self, research_results: List[str], original_request: str) -> str:
        """分析研究结果"""
        self.status = AgentStatus.BUSY
        self._print_progress(f"开始分析 {len(research_results)} 个研究结果", "ANALYSIS")
        
        try:
            self._print_progress("正在构建分析提示...", "PROGRESS")
            analysis_prompt = f"""
你是一个专业的分析专家。请基于以下研究结果进行深度分析:

原始请求: {original_request}

研究结果:
{chr(10).join(research_results)}

请提供:
1. 关键发现和洞察
2. 趋势分析
3. 优缺点评估
4. 未来展望
5. 实用建议

请用结构化的方式组织你的分析。
"""

            self._print_progress("正在调用LLM进行分析...", "PROGRESS")
            messages = [
                SystemMessage(content=analysis_prompt),
                HumanMessage(content="请分析这些研究结果")
            ]
            
            response = self.llm.invoke(messages)
            analysis_result = response.content
            
            self._print_progress("分析任务完成", "SUCCESS")
            self.status = AgentStatus.COMPLETED
            return analysis_result
            
        except Exception as e:
            self._print_progress(f"分析任务失败: {e}", "ERROR")
            self.status = AgentStatus.ERROR
            return f"分析执行失败: {str(e)}"


class SynthesisAgent:
    """综合 Agent - 负责生成最终报告"""
    
    def __init__(self, config: Configuration, verbose: bool = False):
        self.config = config
        self.verbose = verbose
        self.status = AgentStatus.IDLE
        self.llm = self._get_llm()
        
    def _print_progress(self, message: str, level: str = "INFO"):
        """打印进度信息"""
        if self.verbose:
            icons = {
                "INFO": "ℹ️",
                "SUCCESS": "✅", 
                "WARNING": "⚠️",
                "ERROR": "❌",
                "PROGRESS": "🔄",
                "TASK": "📋",
                "RESEARCH": "🔍",
                "ANALYSIS": "🧠",
                "SYNTHESIS": "📝"
            }
            icon = icons.get(level, "ℹ️")
            print(f"{icon} [SynthesisAgent] {message}")
    
    def _get_llm(self):
        """获取 LLM 实例"""
        if self.config.llm_provider == "openai":
            return ChatOpenAI(
                model=self.config.local_llm,
                base_url=self.config.openai_base_url,
                temperature=0.3
            )
        else:
            return ChatOllama(
                model=self.config.local_llm,
                base_url=self.config.ollama_base_url,
                temperature=0.3
            )
    
    async def synthesize_final_report(self, 
                                    research_results: List[str], 
                                    analysis_results: List[str],
                                    original_request: str) -> str:
        """生成最终综合报告"""
        self.status = AgentStatus.BUSY
        self._print_progress(f"开始生成最终综合报告", "SYNTHESIS")
        
        try:
            self._print_progress("正在构建综合报告提示...", "PROGRESS")
            synthesis_prompt = f"""
你是一个专业的报告撰写专家。请基于以下信息生成一份完整的综合报告:

原始请求: {original_request}

研究结果:
{chr(10).join(research_results)}

分析结果:
{chr(10).join(analysis_results)}

请生成一份结构化的最终报告，包括:
1. 执行摘要
2. 详细分析
3. 关键发现
4. 结论和建议
5. 参考资料

报告应该专业、全面、易读。
"""

            self._print_progress("正在调用LLM生成综合报告...", "PROGRESS")
            messages = [
                SystemMessage(content=synthesis_prompt),
                HumanMessage(content="请生成最终综合报告")
            ]
            
            response = self.llm.invoke(messages)
            final_report = response.content
            
            self._print_progress("综合报告生成完成", "SUCCESS")
            self.status = AgentStatus.COMPLETED
            return final_report
            
        except Exception as e:
            self._print_progress(f"综合报告生成失败: {e}", "ERROR")
            self.status = AgentStatus.ERROR
            return f"报告生成失败: {str(e)}"


# LangGraph 节点函数
def decompose_request_node(state: SupervisoryState, config: RunnableConfig) -> Dict[str, Any]:
    """任务分解节点"""
    supervisory_config = Configuration.from_runnable_config(config)
    verbose = config.get("configurable", {}).get("verbose", False)
    supervisory_agent = SupervisoryAgent(supervisory_config, verbose=verbose)
    
    supervisory_agent._print_progress("开始任务分解阶段", "TASK")
    tasks = supervisory_agent.decompose_request(state.user_request)
    
    return {
        "tasks": tasks,
        "current_task_index": 0,
        "messages": state.messages + [AIMessage(content=f"已将请求分解为 {len(tasks)} 个任务")]
    }


def execute_research_node(state: SupervisoryState, config: RunnableConfig) -> Dict[str, Any]:
    """执行研究节点"""
    supervisory_config = Configuration.from_runnable_config(config)
    verbose = config.get("configurable", {}).get("verbose", False)
    research_agent = DeepResearcherAgent(supervisory_config, verbose=verbose)
    
    # 找到研究任务
    research_tasks = [task for task in state.tasks if task.type == TaskType.RESEARCH]
    
    if not research_tasks:
        return {
            "deep_researcher_status": AgentStatus.ERROR,
            "research_results": [],
            "messages": state.messages + [AIMessage(content="未找到研究任务")]
        }
    
    # 执行研究任务
    research_results = []
    for task in research_tasks:
        result = asyncio.run(research_agent.execute_research(task))
        research_results.append(result)
    
    return {
        "deep_researcher_status": AgentStatus.COMPLETED,
        "research_results": research_results,
        "messages": state.messages + [AIMessage(content=f"完成 {len(research_results)} 个研究任务")]
    }


def analyze_results_node(state: SupervisoryState, config: RunnableConfig) -> Dict[str, Any]:
    """分析结果节点"""
    supervisory_config = Configuration.from_runnable_config(config)
    verbose = config.get("configurable", {}).get("verbose", False)
    analysis_agent = AnalysisAgent(supervisory_config, verbose=verbose)
    
    analysis_results = []
    if state.research_results:
        result = asyncio.run(analysis_agent.analyze_results(state.research_results, state.user_request))
        analysis_results.append(result)
    
    return {
        "analysis_agent_status": AgentStatus.COMPLETED,
        "analysis_results": analysis_results,
        "messages": state.messages + [AIMessage(content="完成结果分析")]
    }


def synthesize_final_report_node(state: SupervisoryState, config: RunnableConfig) -> Dict[str, Any]:
    """生成最终报告节点"""
    supervisory_config = Configuration.from_runnable_config(config)
    verbose = config.get("configurable", {}).get("verbose", False)
    synthesis_agent = SynthesisAgent(supervisory_config, verbose=verbose)
    
    final_report = ""
    if state.research_results and state.analysis_results:
        final_report = asyncio.run(synthesis_agent.synthesize_final_report(
            state.research_results,
            state.analysis_results,
            state.user_request
        ))
    
    return {
        "final_synthesis": final_report,
        "messages": state.messages + [AIMessage(content="生成最终综合报告")]
    }


def route_next_task(state: SupervisoryState, config: RunnableConfig) -> Literal["execute_research", "analyze_results", "synthesize_final_report", "end"]:
    """路由到下一个任务"""
    if state.deep_researcher_status == AgentStatus.IDLE:
        return "execute_research"
    elif state.deep_researcher_status == AgentStatus.COMPLETED and state.analysis_agent_status == AgentStatus.IDLE:
        return "analyze_results"
    elif state.analysis_agent_status == AgentStatus.COMPLETED:
        return "synthesize_final_report"
    else:
        return "end"


# 构建主管架构图
def create_supervisory_graph():
    """创建主管架构图"""
    builder = StateGraph(
        SupervisoryState,
        input=SupervisoryStateInput,
        output=SupervisoryStateOutput,
        config_schema=Configuration,
    )
    
    # 添加节点
    builder.add_node("decompose_request", decompose_request_node)
    builder.add_node("execute_research", execute_research_node)
    builder.add_node("analyze_results", analyze_results_node)
    builder.add_node("synthesize_final_report", synthesize_final_report_node)
    
    # 添加边
    builder.add_edge(START, "decompose_request")
    builder.add_conditional_edges(
        "decompose_request",
        route_next_task,
        {
            "execute_research": "execute_research",
            "analyze_results": "analyze_results",
            "synthesize_final_report": "synthesize_final_report",
            "end": END
        }
    )
    builder.add_conditional_edges(
        "execute_research",
        route_next_task,
        {
            "analyze_results": "analyze_results",
            "synthesize_final_report": "synthesize_final_report",
            "end": END
        }
    )
    builder.add_conditional_edges(
        "analyze_results",
        route_next_task,
        {
            "synthesize_final_report": "synthesize_final_report",
            "end": END
        }
    )
    builder.add_edge("synthesize_final_report", END)
    
    return builder.compile()


# 创建主管架构图实例
supervisory_graph = create_supervisory_graph()


# 便捷函数
async def run_supervisory_research(user_request: str, config: Configuration, verbose: bool = False) -> SupervisoryStateOutput:
    """运行主管架构研究"""
    input_state = SupervisoryStateInput(user_request=user_request)
    config_dict = {
        "configurable": {
            **config.dict(),
            "verbose": verbose
        }
    }
    
    # 使用异步调用避免事件循环冲突
    result = await supervisory_graph.ainvoke(input_state, config=config_dict)
    return SupervisoryStateOutput(
        final_synthesis=result.get("final_synthesis", ""),
        research_results=result.get("research_results", []),
        analysis_results=result.get("analysis_results", [])
    )
