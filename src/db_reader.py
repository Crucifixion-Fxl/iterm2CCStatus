"""
cc-switch SQLite database reader module.

Reads LLM usage statistics recorded by the cc-switch proxy tool.
Database location: ~/.cc-switch/cc-switch.db
"""

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# Database path
DB_PATH = Path.home() / ".cc-switch" / "cc-switch.db"


@dataclass
class UsageSummary:
    """LLM usage statistics summary."""
    total_calls: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    successful_calls: int
    failed_calls: int


def get_db_connection() -> Optional[sqlite3.Connection]:
    """
    Get a database connection.

    Returns:
        sqlite3.Connection: Database connection, or None on failure.
    """
    if not DB_PATH.exists():
        return None

    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


def get_usage_summary(
    app_type: str = "claude",
    days: int = 0,
    hours: int = 0
) -> Optional[UsageSummary]:
    """
    Get LLM usage statistics summary.

    Args:
        app_type: App type filter (e.g. "claude", "codex", "opencode").
        days: Filter last N days.
        hours: Filter last N hours.

    Returns:
        UsageSummary: Usage statistics summary, or None on failure.
    """
    conn = get_db_connection()
    if conn is None:
        return None

    try:
        # Build query conditions
        conditions = ["app_type = ?"]
        params = [app_type]

        if days > 0 or hours > 0:
            if days > 0:
                time_delta = timedelta(days=days)
            else:
                time_delta = timedelta(hours=hours)
            cutoff_time = datetime.now() - time_delta
            # created_at is Unix timestamp (integer)
            cutoff_timestamp = int(cutoff_time.timestamp())
            conditions.append("created_at >= ?")
            params.append(cutoff_timestamp)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT
                COUNT(*) as total_calls,
                COALESCE(SUM(input_tokens), 0) as input_tokens,
                COALESCE(SUM(output_tokens), 0) as output_tokens,
                COALESCE(SUM(input_tokens + output_tokens), 0) as total_tokens,
                SUM(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 ELSE 0 END) as successful_calls,
                SUM(CASE WHEN status_code < 200 OR status_code >= 300 THEN 1 ELSE 0 END) as failed_calls
            FROM proxy_request_logs
            WHERE {where_clause}
        """

        cursor = conn.execute(query, params)
        row = cursor.fetchone()

        if row:
            return UsageSummary(
                total_calls=row["total_calls"],
                input_tokens=row["input_tokens"],
                output_tokens=row["output_tokens"],
                total_tokens=row["total_tokens"],
                successful_calls=row["successful_calls"],
                failed_calls=row["failed_calls"]
            )

        return None

    except sqlite3.Error:
        return None
    finally:
        conn.close()


def get_today_usage(app_type: str = "claude") -> Optional[UsageSummary]:
    """Get today's usage statistics."""
    return get_usage_summary(app_type=app_type, days=1)


def get_last_n_days_usage(
    app_type: str = "claude",
    days: int = 30
) -> Optional[UsageSummary]:
    """Get usage summary for the last N days."""
    return get_usage_summary(app_type=app_type, days=days)


def get_current_provider(app_type: str = "claude") -> Optional[tuple]:
    """
    Get current selected provider from cc-switch DB (providers table, is_current=1).

    Returns:
        (id, name) or None if no current provider or table missing.
    """
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        cursor = conn.execute(
            "SELECT id, name FROM providers WHERE app_type = ? AND is_current = 1 LIMIT 1",
            (app_type,),
        )
        row = cursor.fetchone()
        if row:
            return (row["id"], row["name"])
        return None
    except sqlite3.Error:
        return None
    finally:
        conn.close()


def format_tokens(tokens: int) -> str:
    """
    Format token count into human-readable form.

    Args:
        tokens: Token count.

    Returns:
        str: Formatted string.
    """
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    elif tokens >= 1_000:
        return f"{tokens / 1_000:.1f}K"
    else:
        return str(tokens)


def format_status_text(
    usage: Optional[UsageSummary],
    include_cost: bool = False
) -> str:
    """
    Format status bar display text.

    Args:
        usage: Usage statistics.
        include_cost: Whether to include cost information.

    Returns:
        str: Formatted status bar text.
    """
    if usage is None:
        return "LLM: --"

    tokens_str = format_tokens(usage.total_tokens)
    text = f"🤖 {usage.total_calls} calls | {tokens_str} tokens"

    return text