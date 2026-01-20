import sys
from pathlib import Path

# Add project root and src to path for direct script execution
project_root = Path(__file__).resolve().parent.parent.parent
src_root = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

from langchain.agents import create_agent
from main import model
from prompts.format import FORMATTING_AGENT_PROMPT

formatter_agent = create_agent(
    model = model,
    system_prompt = FORMATTING_AGENT_PROMPT
)