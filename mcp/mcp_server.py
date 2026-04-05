"""
MDEB Personal App — MCP server (stdio transport).

Exposes read-only tools that proxy calls to the FastAPI backend.
Intended to be spawned by Claude Desktop as a local subprocess.

Environment variables:
  MDEB_API_URL  — backend base URL (default: http://localhost:8000)
"""
import json
import os
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = os.getenv("MDEB_API_URL", "http://localhost:8000").rstrip("/")
mcp = FastMCP("mdeb-personal-app")


# ── HTTP helper ────────────────────────────────────────────────────────────────

async def _get(path: str, params: dict | None = None) -> object:
    clean_params = {k: v for k, v in (params or {}).items() if v is not None} or None
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(f"{BASE_URL}{path}", params=clean_params)
            r.raise_for_status()
            return r.json()
    except httpx.ConnectError:
        return {"error": f"Cannot connect to backend at {BASE_URL}. Is the backend service running?"}
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}


def _dump(data: object) -> str:
    return json.dumps(data, indent=2, default=str)


# ── Tasks ──────────────────────────────────────────────────────────────────────

@mcp.tool()
async def tasks_list(
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    project_id: Optional[int] = None,
) -> str:
    """List tasks. Filter by status (TODO/IN_PROGRESS/WAITING/COMPLETE/BACKLOG), category_id, or project_id."""
    return _dump(await _get("/api/tasks", {"status": status, "category_id": category_id, "project_id": project_id}))


@mcp.tool()
async def task_get(task_id: int) -> str:
    """Get full details of a single task including its notes."""
    return _dump(await _get(f"/api/tasks/{task_id}"))


@mcp.tool()
async def tasks_list_categories() -> str:
    """List all task categories with their colors."""
    return _dump(await _get("/api/categories"))


@mcp.tool()
async def tasks_list_projects() -> str:
    """List all projects."""
    return _dump(await _get("/api/projects"))


# ── Journal ────────────────────────────────────────────────────────────────────

@mcp.tool()
async def journal_get(date: str) -> str:
    """Get the journal entry for a specific date (YYYY-MM-DD). Returns an error object if no entry exists."""
    return _dump(await _get(f"/api/journal/{date}"))


@mcp.tool()
async def journal_list_dates() -> str:
    """Return all dates that have a journal entry, as a list of ISO date strings."""
    return _dump(await _get("/api/journal/dates"))


@mcp.tool()
async def journal_on_this_day(month: int, day: int, exclude_year: Optional[int] = None) -> str:
    """Return all journal entries from previous years on the same month and day (anniversary / on-this-day view)."""
    return _dump(await _get("/api/journal/on-this-day", {"month": month, "day": day, "exclude_year": exclude_year}))


@mcp.tool()
async def day_rating_get(date: str) -> str:
    """Get the day rating (1–5 stars) for a specific date (YYYY-MM-DD). Returns an error object if no rating exists."""
    return _dump(await _get(f"/api/day-ratings/{date}"))


# ── Notes ──────────────────────────────────────────────────────────────────────

@mcp.tool()
async def notes_list_folders() -> str:
    """List note folders as a tree with note counts per folder."""
    return _dump(await _get("/api/notes/folders"))


@mcp.tool()
async def notes_list(folder_id: Optional[str] = None) -> str:
    """List note summaries (title + metadata, no content). Pass folder_id as an integer string, or 'unfiled' for notes without a folder."""
    return _dump(await _get("/api/notes", {"folder_id": folder_id} if folder_id else None))


@mcp.tool()
async def note_get(note_id: int) -> str:
    """Get the full content of a specific note by ID."""
    return _dump(await _get(f"/api/notes/{note_id}"))


# ── Finance ────────────────────────────────────────────────────────────────────

@mcp.tool()
async def finance_accounts_list() -> str:
    """List all financial accounts (types: debit, credit, investment, other)."""
    return _dump(await _get("/api/finance/accounts"))


@mcp.tool()
async def finance_categories_list() -> str:
    """List all finance categories (type: credit=expense, debit=income, transfer=internal)."""
    return _dump(await _get("/api/finance/categories"))


@mcp.tool()
async def finance_transactions_list(
    year: Optional[int] = None,
    month: Optional[int] = None,
    account_id: Optional[int] = None,
) -> str:
    """List transactions ordered by date descending. Optionally filter by year, month (1–12), and/or account_id."""
    return _dump(await _get("/api/finance/transactions", {"year": year, "month": month, "account_id": account_id}))


@mcp.tool()
async def finance_monthly_summary(year: int, month: int) -> str:
    """Get the full financial summary for a month: per-account balance deltas, per-category totals, and profit (profit-eligible accounts only)."""
    return _dump(await _get("/api/finance/summary", {"year": year, "month": month}))


# ── Time Tracking ──────────────────────────────────────────────────────────────

@mcp.tool()
async def time_entries_list(month: str) -> str:
    """List time tracking entries grouped by day for a given month. month must be YYYY-MM format (e.g. '2025-03')."""
    return _dump(await _get("/api/time/entries", {"month": month}))


@mcp.tool()
async def time_monthly_summary(month: str) -> str:
    """Get time tracking totals per category for a month. month must be YYYY-MM format (e.g. '2025-03')."""
    return _dump(await _get("/api/time/summary", {"month": month}))


# ── Health ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def health_logs_list(start: Optional[str] = None, end: Optional[str] = None) -> str:
    """List health logs (steps, sleep score, resting HR, stress, body battery, intensity minutes). Optionally filter by start and/or end date (YYYY-MM-DD)."""
    return _dump(await _get("/api/health/logs", {"start": start, "end": end}))


@mcp.tool()
async def health_log_get(date: str) -> str:
    """Get the health log for a specific date (YYYY-MM-DD)."""
    return _dump(await _get(f"/api/health/logs/{date}"))


# ── Timeline ───────────────────────────────────────────────────────────────────

@mcp.tool()
async def timeline_month_overview(year: int, month: int) -> str:
    """Get a calendar-grid overview for a month showing which days have journal entries, transactions, completed tasks, time entries, and health logs. Best starting point for 'what happened this month'."""
    return _dump(await _get("/api/timeline/month-overview", {"year": year, "month": month}))


@mcp.tool()
async def timeline_day_profile(date: str) -> str:
    """Get the full profile for a single day (YYYY-MM-DD): journal entry, day rating, all transactions, completed tasks, time entries, and health log — all in one call."""
    return _dump(await _get(f"/api/timeline/day/{date}"))


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run(transport="stdio")
