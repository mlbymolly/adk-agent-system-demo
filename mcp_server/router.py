"""Agent Router MCP Server.

Exposes tools that analyze user queries and recommend the optimal
sub-agent routing strategy for the multi-agent system.

Routing strategies:
  - keyword:  Fast rule-based matching on trigger words.
  - semantic: Cosine similarity between query and agent descriptions.
  - hybrid:   Weighted combination of keyword + semantic scores.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Agent registry
# ---------------------------------------------------------------------------

@dataclass
class AgentInfo:
    name: str
    description: str
    keywords: list[str] = field(default_factory=list)


AGENTS: list[AgentInfo] = [
    AgentInfo(
        name="date_agent",
        description="Handles questions about dates, time, day of week, and calendar information",
        keywords=[
            "date", "time", "today", "tomorrow", "yesterday", "day",
            "week", "month", "year", "calendar", "clock", "when",
        ],
    ),
    AgentInfo(
        name="weather_agent",
        description="Handles questions about weather conditions and forecasts for locations",
        keywords=[
            "weather", "temperature", "rain", "sunny", "cloudy", "storm",
            "forecast", "humidity", "wind", "snow", "hot", "cold", "climate",
        ],
    ),
    AgentInfo(
        name="task_agent",
        description="Handles task management including CRUD operations, analytics, overdue tracking, and search",
        keywords=[
            "task", "todo", "create", "delete", "update", "complete",
            "overdue", "due", "priority", "pending", "list", "show",
            "statistics", "stats", "search", "assign", "manage",
        ],
    ),
]

AGENT_MAP = {a.name: a for a in AGENTS}

# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Lowercase split on non-alpha characters."""
    return re.findall(r"[a-z]+", text.lower())


def _keyword_scores(query: str) -> dict[str, float]:
    """Return a normalised keyword-match score per agent (0-1)."""
    tokens = set(_tokenize(query))
    raw: dict[str, int] = {}
    for agent in AGENTS:
        raw[agent.name] = sum(1 for kw in agent.keywords if kw in tokens)
    total = sum(raw.values()) or 1
    return {name: count / total for name, count in raw.items()}


def _term_freq(tokens: list[str]) -> dict[str, float]:
    """Simple term-frequency vector."""
    freq: dict[str, float] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    length = math.sqrt(sum(v * v for v in freq.values())) or 1
    return {k: v / length for k, v in freq.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    keys = set(a) & set(b)
    if not keys:
        return 0.0
    return sum(a[k] * b[k] for k in keys)


def _semantic_scores(query: str) -> dict[str, float]:
    """Cosine similarity between query TF vector and each agent description."""
    q_vec = _term_freq(_tokenize(query))
    scores: dict[str, float] = {}
    for agent in AGENTS:
        desc_vec = _term_freq(_tokenize(agent.description))
        scores[agent.name] = round(_cosine(q_vec, desc_vec), 4)
    return scores


def _hybrid_scores(
    query: str,
    keyword_weight: float = 0.6,
    semantic_weight: float = 0.4,
) -> dict[str, float]:
    """Weighted combination of keyword and semantic scores."""
    kw = _keyword_scores(query)
    sem = _semantic_scores(query)
    combined: dict[str, float] = {}
    for name in kw:
        combined[name] = round(
            keyword_weight * kw[name] + semantic_weight * sem[name], 4
        )
    return combined


def _pick_best(scores: dict[str, float]) -> str:
    return max(scores, key=scores.get)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "agent-router",
    instructions=(
        "This server helps pick the optimal sub-agent for a user query. "
        "Use `analyze_query` to classify a single query, `compare_strategies` "
        "to see how different routing methods score, `list_agents` to see "
        "available agents, and `batch_route` to classify many queries at once."
    ),
)


@mcp.tool()
def list_agents() -> list[dict]:
    """Return all registered sub-agents with their descriptions and keywords."""
    return [
        {
            "name": a.name,
            "description": a.description,
            "keywords": a.keywords,
        }
        for a in AGENTS
    ]


@mcp.tool()
def analyze_query(
    query: str,
    strategy: str = "hybrid",
) -> dict:
    """Classify a user query and recommend which sub-agent should handle it.

    Args:
        query: The user's natural-language message.
        strategy: Routing strategy — one of 'keyword', 'semantic', or 'hybrid'.

    Returns:
        A dict with the recommended agent, confidence scores, and strategy used.
    """
    strategy = strategy.lower()
    if strategy == "keyword":
        scores = _keyword_scores(query)
    elif strategy == "semantic":
        scores = _semantic_scores(query)
    else:
        strategy = "hybrid"
        scores = _hybrid_scores(query)

    best = _pick_best(scores)
    return {
        "query": query,
        "strategy": strategy,
        "recommended_agent": best,
        "confidence": scores[best],
        "all_scores": scores,
    }


@mcp.tool()
def compare_strategies(query: str) -> dict:
    """Run all three routing strategies on a query and compare results.

    Args:
        query: The user's natural-language message.

    Returns:
        Per-strategy scores and the overall recommended agent.
    """
    results: dict[str, dict] = {}
    for name, fn in [
        ("keyword", _keyword_scores),
        ("semantic", _semantic_scores),
        ("hybrid", _hybrid_scores),
    ]:
        scores = fn(query)
        best = _pick_best(scores)
        results[name] = {"scores": scores, "recommended": best}

    # Overall recommendation = hybrid winner
    overall = results["hybrid"]["recommended"]
    return {
        "query": query,
        "strategies": results,
        "recommended_agent": overall,
    }


@mcp.tool()
def batch_route(
    queries: list[str],
    strategy: str = "hybrid",
) -> list[dict]:
    """Classify multiple queries at once.

    Args:
        queries: List of user messages to classify.
        strategy: Routing strategy to use for all queries.

    Returns:
        A list of routing results, one per query.
    """
    return [analyze_query(query, strategy) for query in queries]

if __name__ == "__main__":
    mcp.run()
