"""
ArXiv Search Tool - Robust integration with ArXiv academic repository.

Features:
- Retry logic for transient failures
- Proper API client usage
- Intelligent result formatting
- Handles edge cases (many authors, long abstracts)
"""
import sys
from pathlib import Path

# Add project root to path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import arxiv
from typing import Optional
from langchain_core.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def _format_authors(authors: list, max_authors: int = 3) -> str:
    """Format author list with 'et al.' for long lists."""
    author_names = [author.name for author in authors]
    
    if len(author_names) <= max_authors:
        return ", ".join(author_names)
    else:
        return f"{', '.join(author_names[:max_authors])}, et al."


def _truncate_text(text: str, max_length: int = 300) -> str:
    """Truncate text to max_length while preserving word boundaries."""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:
        truncated = truncated[:last_space]
    
    return truncated.rstrip('.,;:') + "..."


def _format_paper_result(paper) -> dict:
    """Format a single paper result into a structured dictionary."""
    return {
        "title": paper.title,
        "authors": _format_authors(paper.authors),
        "authors_full": [author.name for author in paper.authors],
        "published": paper.published.strftime("%Y-%m-%d"),
        "year": paper.published.year,
        "updated": paper.updated.strftime("%Y-%m-%d"),
        "abstract": _truncate_text(paper.summary, 300),
        "url": paper.entry_id,
        "pdf_url": paper.pdf_url,
        "categories": paper.categories,
        "primary_category": paper.primary_category,
    }


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True
)
def _execute_arxiv_search(client: arxiv.Client, search: arxiv.Search) -> list:
    """Execute ArXiv search with retry logic."""
    return list(client.results(search))


@tool
def search_arxiv(query: str, max_results: int = 10) -> str:
    """
    Search the ArXiv database for academic papers.
    
    This tool searches ArXiv for papers matching the query, returning
    structured information including title, authors, abstract, publication
    date, and links. Results are sorted by submission date (most recent first).
    
    Args:
        query: The search query (supports ArXiv query syntax like 'cat:cs.AI' for categories)
        max_results: Maximum number of results to return (default: 10, max: 50)
    
    Returns:
        A formatted string with paper details or an error message.
    """
    if not query or not query.strip():
        return "Error: Query cannot be empty"
    
    max_results = min(max(1, max_results), 50)
    
    try:
        client = arxiv.Client(
            page_size=max_results,
            delay_seconds=1.0,
            num_retries=3
        )
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = _execute_arxiv_search(client, search)
        
        if not papers:
            return f"No papers found matching query: '{query}'"
        
        formatted_papers = [_format_paper_result(paper) for paper in papers]
        
        # Format output as readable text
        output_lines = [f"Found {len(formatted_papers)} papers for query: '{query}'\n"]
        
        for i, paper in enumerate(formatted_papers, 1):
            output_lines.append(f"--- Paper {i} ---")
            output_lines.append(f"Title: {paper['title']}")
            output_lines.append(f"Authors: {paper['authors']}")
            output_lines.append(f"Published: {paper['published']}")
            output_lines.append(f"Categories: {paper['categories']}")
            output_lines.append(f"Primary Category: {paper['primary_category']}")
            output_lines.append(f"Abstract: {paper['abstract']}")
            output_lines.append(f"URL: {paper['url']}")
            output_lines.append(f"PDF: {paper['pdf_url']}")
            output_lines.append("")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Search failed: {str(e)}"


@tool
def search_arxiv_advanced(
    query: str,
    max_results: int = 10,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    categories: Optional[str] = None
) -> str:
    """
    Advanced ArXiv search with filtering options.
    
    Provides advanced search capabilities including date range filtering
    and category restrictions. Useful for finding recent papers or papers
    in specific research areas.
    
    Args:
        query: The search query
        max_results: Maximum number of results (default: 10, max: 50)
        year_from: Filter papers published from this year onwards (e.g., 2023)
        year_to: Filter papers published up to this year (e.g., 2025)
        categories: Comma-separated ArXiv categories (e.g., 'cs.AI,cs.LG,cs.CL')
    
    Returns:
        A formatted string with filtered paper details.
    
    Example categories:
        cs.AI - Artificial Intelligence
        cs.LG - Machine Learning  
        cs.CL - Computation and Language (NLP)
        cs.CV - Computer Vision
        stat.ML - Machine Learning (Statistics)
    """
    enhanced_query = query
    
    if categories:
        cat_list = [c.strip() for c in categories.split(',')]
        cat_filter = " OR ".join([f"cat:{cat}" for cat in cat_list])
        enhanced_query = f"({query}) AND ({cat_filter})"
    
    # Search with more results to allow filtering
    search_max = min(max_results * 3, 100)
    
    try:
        client = arxiv.Client(
            page_size=search_max,
            delay_seconds=1.0,
            num_retries=3
        )
        
        search = arxiv.Search(
            query=enhanced_query,
            max_results=search_max,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        papers = _execute_arxiv_search(client, search)
        
        if not papers:
            return f"No papers found matching query: '{query}' with filters"
        
        formatted_papers = [_format_paper_result(paper) for paper in papers]
        
        # Apply year filters
        if year_from:
            formatted_papers = [p for p in formatted_papers if p["year"] >= year_from]
        
        if year_to:
            formatted_papers = [p for p in formatted_papers if p["year"] <= year_to]
        
        # Limit results
        formatted_papers = formatted_papers[:max_results]
        
        if not formatted_papers:
            return f"No papers found matching query: '{query}' with year filter {year_from}-{year_to}"
        
        # Format output
        filters_desc = []
        if year_from:
            filters_desc.append(f"from {year_from}")
        if year_to:
            filters_desc.append(f"to {year_to}")
        if categories:
            filters_desc.append(f"categories: {categories}")
        
        filter_str = f" (Filters: {', '.join(filters_desc)})" if filters_desc else ""
        
        output_lines = [f"Found {len(formatted_papers)} papers for query: '{query}'{filter_str}\n"]
        
        for i, paper in enumerate(formatted_papers, 1):
            output_lines.append(f"--- Paper {i} ---")
            output_lines.append(f"Title: {paper['title']}")
            output_lines.append(f"Authors: {paper['authors']}")
            output_lines.append(f"Published: {paper['published']}")
            output_lines.append(f"Category: {paper['primary_category']}")
            output_lines.append(f"Abstract: {paper['abstract']}")
            output_lines.append(f"URL: {paper['url']}")
            output_lines.append("")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Advanced search failed: {str(e)}"


# Utility function to get raw paper data (for other tools)
def get_papers_data(query: str, max_results: int = 10) -> list[dict]:
    """Get raw paper data as list of dictionaries (for internal use)."""
    try:
        client = arxiv.Client(page_size=max_results, delay_seconds=1.0, num_retries=3)
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        papers = _execute_arxiv_search(client, search)
        return [_format_paper_result(p) for p in papers]
    except Exception:
        return []
