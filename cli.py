import sys
from pathlib import Path

import questionary
import typer
from rich.console import Console
from rich.panel import Panel

# Add project root and src to path for direct execution
project_root = Path(__file__).resolve().parent
src_root = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_root))

from agents.analyst_agent import analyst_agent
from agents.formatter_agent import formatter_agent
from agents.researcher_agent import research_agent


def _extract_last_assistant_text(result: object) -> str:
    if isinstance(result, str):
        return result
    if isinstance(result, dict) and result.get("messages"):
        last = result["messages"][-1]
        return getattr(last, "content", None) or last.get("content", str(last))
    return str(result)


def _invoke_agent(agent, user_content: str) -> str:
    res = agent.invoke({"messages": [{"role": "user", "content": user_content}]})
    return _extract_last_assistant_text(res)


app = typer.Typer(
    add_completion=False,
    help="Run Research OS from the command line.",
)
console = Console()


def _print_section(title: str, body: str) -> None:
    content = body.strip() if body.strip() else "(no output)"
    console.print(Panel(content, title=title, expand=False))


@app.command()
def run() -> None:
    print(
       ''' 
        ██████╗ ███████╗███████╗███████╗ █████╗ ██████╗  ██████╗██╗  ██╗
        ██╔══██╗██╔════╝██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║ 
        ██████╔╝█████╗  ███████╗█████╗  ███████║██████╔╝██║     ███████║
        ██╔══██╗██╔══╝  ╚════██║██╔══╝  ██╔══██║██╔══██╗██║     ██╔══██║
        ██║  ██║███████╗███████║███████╗██║  ██║██║  ██║╚██████╗██║  ██║
        ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
               Research OS - your arXiv research assistant.
'''
    )
    while True:
        query = questionary.text(
            "Research question",
            instruction="Ask about a topic, include keywords or categories.",
        ).ask()
        if query is None or not query.strip():
            console.print("No query provided. Exiting.")
            return
        query = query.strip()

        show_intermediate = questionary.confirm(
            "Show intermediate outputs?",
            default=True,
        ).ask()
        if show_intermediate is None:
            console.print("No selection made. Exiting.")
            return

        console.print("[bold]Running research flow...[/bold]")
        with console.status("Researching..."):
            research_output = _invoke_agent(research_agent, query)
        with console.status("Analyzing..."):
            analysis_output = _invoke_agent(analyst_agent, research_output)
        with console.status("Formatting citations..."):
            citations_output = _invoke_agent(formatter_agent, research_output)

        if show_intermediate:
            _print_section("Research", research_output)
            _print_section("Analysis", analysis_output)
        else:
            console.print("(Intermediate outputs hidden.)")

        _print_section("Citations", citations_output)
        if questionary.confirm(
            "Run another research?",
            default=True,
        ).ask():
            continue
        else:
            break


if __name__ == "__main__":
    app()
