from langchain_core.tools import tool
from datetime import datetime

@tool
def get_current_datetime() -> str:
    """Get the current date and time in ISO format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")