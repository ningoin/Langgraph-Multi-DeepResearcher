import operator
from dataclasses import dataclass, field
from typing_extensions import Annotated


@dataclass(kw_only=True)
class SummaryState:
    research_topic: str = field(default=None)  # 研究主题
    search_query: str = field(default=None)  # 搜索查询
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
    research_loop_count: int = field(default=0)  # Research loop count
    running_summary: str = field(default=None)  # Final report


@dataclass(kw_only=True)
class SummaryStateInput:
    research_topic: str = field(default=None)  # 研究主题


@dataclass(kw_only=True)
class SummaryStateOutput:
    running_summary: str = field(default=None)  # 输出报告
