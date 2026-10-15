# coreautopost

Headless Discord automation engine with TLS fingerprint impersonation, dynamic header synthesis, in-memory session management, and cloud attachment streaming.

## Overview

Automating interactions with Discord client-facing endpoints requires precision across multiple layers. Standard HTTP clients fail Cloudflare bot protection and backend fraud scoring due to mismatched TLS handshakes (JA3/JA4) and static header anomalies.

`coreautopost` defines a lightweight architecture that matches desktop Firefox network characteristics without running a browser engine.

## Core Capabilities

1. TLS Fingerprint Impersonation:
   Matches Firefox cipher suites, elliptic curves, and extension orders at the TLS handshake level via `curl_cffi`.
2. Dynamic Header Synthesis:
   Extracts client build number directly from Discord application bundles and generates `X-Super-Properties` base64 structures dynamically.
3. In-Memory Session Lifecycle:
   Session identifiers (installation ID, client launch ID, launch signature) initialize once per runtime and stay in memory without writing state files to disk.
4. Direct Cloud Attachment Upload:
   Handles Discord multi-step file attachments: requests pre-signed URLs from the Discord API, streams binary data directly to Google Cloud Storage via PUT, and attaches reference IDs to the message payload.
5. Universal Proxy Support:
   Supports HTTP, HTTPS, SOCKS4, and SOCKS5 protocols, with automatic validation against target endpoints.

## Requirements

- Python 3.10+
- `curl_cffi` >= 0.16.0
- `websockets` >= 13.0

## Installation

```bash
git clone https://github.com/yeweroooo/coreautopost.git
cd coreautopost
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Quick Start

### Basic Message

```python
from client import StealthDiscordClient
# or: from coreautopost import StealthDiscordClient

TOKEN = "YOUR_DISCORD_USER_TOKEN"
GUILD_ID = "YOUR_GUILD_ID"
CHANNEL_ID = "YOUR_CHANNEL_ID"

client = StealthDiscordClient(token=TOKEN)

status, response = client.send_message(
    guild_id=GUILD_ID,
    channel_id=CHANNEL_ID,
    content="Hello from coreautopost",
    simulate_typing=True
)

print(f"Status: {status}")
```

### Sending Messages with Attachments

Attachments can be passed as local file paths or in-memory byte tuples:

```python
status, response = client.send_message(
    guild_id=GUILD_ID,
    channel_id=CHANNEL_ID,
    content="Message with multiple attachments",
    files=[
        "/path/to/screenshot.png",
        ("report.json", b'{"status": "ok"}', "application/json")
    ],
    simulate_typing=True
)
```

### Using Proxies

Specify a custom proxy string or use automatic proxy resolution:

```python
# 1. Custom proxy (HTTP, SOCKS4, SOCKS5)
client = StealthDiscordClient(token=TOKEN, proxy="socks5://127.0.0.1:9050")

# 2. Auto-fetch and test free working proxies from ProxyScrape
client = StealthDiscordClient(token=TOKEN, proxy="proxyscrape")

# 3. Rotate proxy during execution
new_proxy = client.rotate_proxyscrape_proxy()
```

## Repository Structure

```
coreautopost/
    ├── __init__.py      # Package exports
    ├── client.py        # StealthDiscordClient orchestrator
    ├── constants.py     # Endpoints, default profiles, epoch values
    ├── session.py       # In-memory session state and Snowflake generator
    ├── builder.py       # Dynamic builders for headers and payload structures
    ├── proxy.py         # Proxy formatting and ProxyScrape auto-tester
    ├── attachment.py    # GCS pre-signed upload handler
    ├── pyproject.toml   # Build configuration
    ├── requirements.txt # Runtime dependencies
    ├── LICENSE          # MIT License
    └── README.md        # Technical documentation
```

## License

MIT License. See [LICENSE](LICENSE) for details.
