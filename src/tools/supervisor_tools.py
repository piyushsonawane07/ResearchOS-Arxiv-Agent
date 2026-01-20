from langchain.tools import tool

from agents.analyst_agent import analyst_agent
from agents.formatter_agent import formatter_agent
from agents.researcher_agent import research_agent


def _extract_last_assistant_text(result: object) -> str:
    """
    Best-effort extraction of the last assistant message content from agent.invoke(...).
    We intentionally return a string so downstream agents receive clean text.
    """
    if isinstance(result, str):
        return result

    if isinstance(result, dict) and "messages" in result and result["messages"]:
        last = result["messages"][-1]
        # LangChain message objects often have `.content`; fallback to dict-style
        return getattr(last, "content", None) or last.get("content", str(last))

    return str(result)

@tool
def request_researcher_agent(query: str) -> str:
    """Request the researcher agent to research the query."""
    res = research_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return _extract_last_assistant_text(res)

@tool
def request_analyst_agent(research_results: str) -> str:
    """Request the analyst agent to analyze the research results."""
    res = analyst_agent.invoke({"messages": [{"role": "user", "content": research_results}]})
    return _extract_last_assistant_text(res)

@tool
def request_formatter_agent(research_results: str) -> str:
    """Request the formatter agent to format research output into citations."""
    res = formatter_agent.invoke({"messages": [{"role": "user", "content": research_results}]})
    return _extract_last_assistant_text(res)
