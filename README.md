# iTerm2 CC Status

iTerm2 status bar component that shows LLM usage statistics (calls and tokens) from the [cc-switch](https://github.com/farion1231/cc-switch) proxy. Displays the current provider and last 30 days usage; click the status bar to see a popover with details.

**[中文说明](README.zh-CN.md)**

---

## Requirements

- **iTerm2** (with Python API enabled)
- **Python 3.6+** — iTerm2 runs this script with your system Python; install from [python.org](https://www.python.org/) or `brew install python3` if needed
- **cc-switch** proxy with SQLite DB at `~/.cc-switch/cc-switch.db`

## How to use in iTerm2

### 1. Install Python and dependencies

Ensure Python 3 is installed (`python3 --version`). Then install the script’s dependencies:

```bash
pip install -r requirements.txt
# or: pip3 install -r requirements.txt
```

### 2. Enable iTerm2 Python API

In iTerm2:

- Open **Preferences** (⌘,) → **General** → **Magic**
- Check **Enable Python API server**

### 3. Install the script

Copy both Python files into iTerm2’s Scripts folder so `db_reader` can be imported:

```bash
# Create Scripts folder if it doesn't exist
mkdir -p "$HOME/Library/Application Support/iTerm2/Scripts"

# Copy both scripts (project root = where you cloned this repo)
cp iterm2_llm_status.py db_reader.py "$HOME/Library/Application Support/iTerm2/Scripts/"
```

### 4. Add the status bar component

1. In iTerm2 menu: **Scripts** → **iterm2_llm_status.py** → **LLM Status**
2. Or: **Scripts** → **Manage** → select **iterm2_llm_status.py** and run **LLM Status**
3. In the status bar area, click **+** (or **Add Component**) and add **LLM (30d)**

The status bar will show something like: `ProviderName · ✦ 42 calls · 1.2K tokens` (refreshed every 3 seconds). Click it to open a popover with provider, calls, and tokens.

## Data source

Statistics are read from the SQLite database created by cc-switch:

- **Path:** `~/.cc-switch/cc-switch.db`
- **Tables used:** `proxy_request_logs`, `providers`

If the database is missing or empty, the component shows `✦ — 0 calls · 0 tokens`.

## Configuration

Edit `iterm2_llm_status.py` to change:

- `APP_TYPE`: app type filter (default `"claude"`)
- `REFRESH_INTERVAL`: status bar refresh interval in seconds (default `3`)

## Files

| File | Description |
|------|-------------|
| `iterm2_llm_status.py` | iTerm2 status bar component entry |
| `db_reader.py` | Reads cc-switch SQLite DB and formats usage stats |

## License

Use and modify as you like.
