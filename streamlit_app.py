import sys
from pathlib import Path

import streamlit as st

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


st.set_page_config(page_title="Research OS", page_icon="📚", layout="wide")

st.title("Research OS")
st.caption(
    "Search papers, analyze trends, and format APA citations in one flow."
)

with st.sidebar:
    st.header("Settings")
    show_intermediate = st.checkbox("Show intermediate outputs", value=True)
    st.markdown(
        "Tip: Use clear keywords or include a category like `cs.AI`."
    )
    st.divider()
    st.write("Example queries")
    st.code("Agentic AI Design Patterns")
    st.code("Multi-agent systems arXiv cs.AI")

query = st.text_area(
    "Research question",
    placeholder="Ask about a topic, include keywords or categories.",
    height=120,
)

actions_left, actions_right = st.columns([1, 1])
with actions_left:
    run_clicked = st.button(
        "Run flow",
        type="primary",
        use_container_width=True,
    )
with actions_right:
    clear_clicked = st.button(
        "Clear outputs",
        use_container_width=True,
    )

tab_names = ["Research", "Analysis", "Citations"]
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Research"
if "stage" not in st.session_state:
    st.session_state["stage"] = "idle"
if "research_output" not in st.session_state:
    st.session_state["research_output"] = ""
if "analysis_output" not in st.session_state:
    st.session_state["analysis_output"] = ""
if "citations_output" not in st.session_state:
    st.session_state["citations_output"] = ""

selected_tab = st.radio(
    "Stage",
    tab_names,
    index=tab_names.index(st.session_state["active_tab"]),
    horizontal=True,
    label_visibility="collapsed",
)
if selected_tab != st.session_state["active_tab"]:
    st.session_state["active_tab"] = selected_tab

if clear_clicked:
    st.session_state["stage"] = "idle"
    st.session_state["active_tab"] = "Research"
    st.session_state["research_output"] = ""
    st.session_state["analysis_output"] = ""
    st.session_state["citations_output"] = ""
    st.rerun()

if run_clicked:
    if not query.strip():
        st.warning("Please enter a research question.")
    else:
        st.session_state["stage"] = "research"
        st.session_state["active_tab"] = "Research"
        st.session_state["research_output"] = ""
        st.session_state["analysis_output"] = ""
        st.session_state["citations_output"] = ""
        st.rerun()

stage = st.session_state["stage"]

stage_progress = {
    "idle": 0,
    "research": 0.33,
    "analysis": 0.66,
    "citations": 0.9,
    "done": 1.0,
}
st.progress(stage_progress.get(stage, 0))

if stage == "research":
    with st.spinner("Researching..."):
        st.session_state["research_output"] = _invoke_agent(
            research_agent, query
        )
    st.session_state["stage"] = "analysis"
    st.session_state["active_tab"] = "Analysis"
    st.rerun()

if stage == "analysis":
    with st.spinner("Analyzing..."):
        st.session_state["analysis_output"] = _invoke_agent(
            analyst_agent, st.session_state["research_output"]
        )
    st.session_state["stage"] = "citations"
    st.session_state["active_tab"] = "Citations"
    st.rerun()

if stage == "citations":
    with st.spinner("Formatting citations..."):
        st.session_state["citations_output"] = _invoke_agent(
            formatter_agent, st.session_state["research_output"]
        )
    st.session_state["stage"] = "done"

if st.session_state["active_tab"] == "Research":
    st.subheader("Research results")
    if show_intermediate:
        st.markdown(
            st.session_state["research_output"] or "_No research output_"
        )
    else:
        st.info("Research output hidden.")

if st.session_state["active_tab"] == "Analysis":
    st.subheader("Analysis summary")
    if show_intermediate:
        st.markdown(
            st.session_state["analysis_output"] or "_No analysis output_"
        )
    else:
        st.info("Analysis output hidden.")

if st.session_state["active_tab"] == "Citations":
    st.subheader("Formatted citations")
    st.markdown(
        st.session_state["citations_output"] or "_No citations output_"
    )
