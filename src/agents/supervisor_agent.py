import sys
from pathlib import Path

# Add project root and src to path for direct script execution
project_root = Path(__file__).resolve().parent.parent.parent
src_root = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

from langchain.agents import create_agent
from main import model
from tools.supervisor_tools import request_researcher_agent, request_analyst_agent, request_formatter_agent

SUPERVISOR_AGENT_PROMPT = """
You are a supervisor agent orchestrating a 3-step research workflow using tools.

## Goal
Given a user's research question, produce a final, high-quality response by coordinating:
1) a research pass (find papers),
2) an analysis pass (compute insights from the research output),
3) a formatting pass (convert paper metadata into APA citations).

## Available tools (must be used in this order)
- `request_researcher_agent(query: str) -> str`
  - Use this FIRST to retrieve paper results and metadata.
- `request_analyst_agent(research_results: str) -> str`
  - Use this SECOND to analyze the research output (e.g., year distribution).
- `request_formatter_agent(research_results: str) -> str`
  - Use this THIRD to format citations from the original research output (not the analysis).

## Operating rules
- Do NOT fabricate papers, metadata, dates, or citations. Only use what the tools return.
- Keep the pipeline tight: call the next tool immediately after you have the prior step's output.
- The formatter needs individual paper metadata (title/authors/published/URL). Use the researcher output for citations.
- If any step output is empty, low quality, or clearly missing what the next step needs:
  - Ask for a targeted retry by calling the appropriate tool again with a more specific instruction.
  - Example: ask the researcher to refine keywords/categories or increase breadth.

## Completion criteria
The job is complete only when you have:
- Research results (papers with titles/authors/published dates/links),
- Analysis derived from that research output,
- Final formatted citations or a clearly formatted final report.

## Final response format
Return a concise final response with these sections (use exactly these headings):

### Research
<paste/condense the researcher output; preserve key metadata>

### Analysis
<paste the analyst output>

### Formatted citations
<paste the formatter output>
"""

supervisor_agent = create_agent(
    model = model,
    system_prompt = SUPERVISOR_AGENT_PROMPT,
    tools = [request_researcher_agent, request_analyst_agent, request_formatter_agent]
)

if __name__ == "__main__":
    query = "Agentic AI Design Patterns"
    for event in supervisor_agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values",
    ):
        event["messages"][-1].pretty_print()
