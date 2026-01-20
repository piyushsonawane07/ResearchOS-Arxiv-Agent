"""
Analyzes research papers and returns a summary of the findings. 
Creates visualizations of the findings.
create summarized report of the findings.
"""

from langchain.agents import create_agent

from main import model
from prompts.analyst import ANALYST_AGENT_PROMPT


analyst_agent = create_agent(
    model = model,
    system_prompt = ANALYST_AGENT_PROMPT
)