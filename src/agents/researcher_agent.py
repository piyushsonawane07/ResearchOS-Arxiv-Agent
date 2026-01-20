import sys
from pathlib import Path

# Add project root and src to path for direct script execution
project_root = Path(__file__).resolve().parent.parent.parent
src_root = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

from langchain.agents import create_agent
from tools.arxiv_tool import search_arxiv, search_arxiv_advanced
from tools.datetime import get_current_datetime
from main import model
from prompts.research import RESEARCH_AGENT_PROMPT


research_agent = create_agent(
    model=model,
    tools = [search_arxiv, search_arxiv_advanced, get_current_datetime],
    system_prompt=RESEARCH_AGENT_PROMPT,
)

if __name__ == "__main__":
    query = "What are the latest research papers on AI?"
    for event in research_agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values",
    ):
        event["messages"][-1].pretty_print()
