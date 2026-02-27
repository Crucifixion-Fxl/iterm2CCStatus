#!/usr/bin/env python3
"""
iTerm2 LLM Usage StatusBar component.

Shows LLM usage stats recorded by cc-switch proxy:
- Claude app usage (calls and tokens)
- Auto-refresh every 3 seconds

Setup:
1. pip install -r requirements.txt
2. Copy script to iTerm2 Python scripts directory:
   cp iterm2_llm_status.py ~/Library/Application Support/iTerm2/Scripts/
3. In iTerm2: Scripts > iterm2_llm_status.py > LLM Status
4. Click "Add Component" to add the status bar component
"""

import iterm2
from db_reader import get_current_provider, get_last_n_days_usage, format_tokens


# Config
APP_TYPE = "claude"  # app_type to monitor
REFRESH_INTERVAL = 3  # refresh interval (seconds)


async def main(connection):
    """iTerm2 StatusBar component main entry."""
    @iterm2.StatusBarRPC
    async def llm_status_coro(knobs):
        """Called by iTerm2 at update_cadence interval; returns status bar text."""
        usage = get_last_n_days_usage(app_type=APP_TYPE, days=30)
        provider = get_current_provider(app_type=APP_TYPE)
        prefix = f"{provider[1]} · " if provider else ""
        if usage:
            total_tokens = usage.input_tokens + usage.output_tokens
            tokens_str = format_tokens(total_tokens)
            return f"{prefix}✦ {usage.total_calls} calls · {tokens_str} tokens"
        return f"{prefix}✦ — 0 calls · 0 tokens"

    async def on_click(session_id: str):
        """Open popover with current stats (no icons)."""
        usage = get_last_n_days_usage(app_type=APP_TYPE, days=30)
        provider = get_current_provider(app_type=APP_TYPE)
        provider_name = provider[1] if provider else "—"
        calls = usage.total_calls if usage else 0
        tokens_str = (
            format_tokens(usage.input_tokens + usage.output_tokens)
            if usage
            else "0"
        )
        html = f"""
        <div style="font-family:system-ui;padding:10px;min-width:140px;font-size:13px;">
            <p style="margin:0 0 6px 0;"><strong>Provider</strong></p>
            <p style="margin:0 0 10px 0;">{provider_name}</p>
            <p style="margin:0 0 6px 0;"><strong>Calls</strong> (30d)</p>
            <p style="margin:0 0 10px 0;">{calls}</p>
            <p style="margin:0 0 6px 0;"><strong>Tokens</strong> (30d)</p>
            <p style="margin:0 0 0 0;">{tokens_str}</p>
        </div>
        """
        await component.async_open_popover(
            session_id, html, iterm2.util.Size(180, 120)
        )

    component = iterm2.StatusBarComponent(
        short_description="LLM (30d)",
        detailed_description="LLM usage (last 30 days): calls and tokens",
        knobs=[],
        exemplar="✦ — 0 calls · 0 tokens",
        update_cadence=REFRESH_INTERVAL,
        identifier="com.user.iterm2.llm-status",
        icons=[],
    )
    await component.async_register(connection, llm_status_coro, onclick=on_click)


# Entry point
if __name__ == "__main__":
    iterm2.run_forever(main)