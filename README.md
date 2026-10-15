# coreautopost

Headless Discord REST client library with browser TLS impersonation, dynamic header generation, in-memory session lifecycle, and attachment upload support.

## Overview

Automating interactions with Discord user endpoints requires matching real browser fingerprints across multiple layers. Standard HTTP clients fail Cloudflare bot management and internal risk scoring due to mismatched TLS handshakes (JA3/JA4) and static header anomalies.

`coreautopost` provides a modular Python implementation that replicates the exact network behavior of desktop Firefox without launching a browser process.

## Key Mechanisms

1. TLS Fingerprint Impersonation:
   Uses `curl_cffi` to match Firefox 135 cipher suites, elliptic curves, and extension orders at the TLS handshake level.
2. Dynamic Header & Super-Properties:
   Extracts client build number directly from Discord application bundles and generates `X-Super-Properties` base64 payloads dynamically.
3. In-Memory Session Lifecycle:
   Session identifiers (installation ID, client launch ID, launch signature) are initialized once when the process starts and reused across subsequent calls in memory without writing state files to disk.
4. Direct Cloud Attachment Upload:
   Handles Discord multi-step file attachments: requests pre-signed URLs from the Discord API, streams binary data directly to Google Cloud Storage via PUT, and binds attachment references to the final message payload.
5. Universal Proxy & Auto-Rotation:
   Supports HTTP, HTTPS, SOCKS4, and SOCKS5 proxies, including integrated automatic fetching and live testing against Discord endpoints using ProxyScrape.

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
from discord_stealth import StealthDiscordClient

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

## Package Architecture

```
discord_stealth/
    ├── constants.py     # Endpoints, default profiles, epoch values
    ├── session.py       # In-memory session state and Snowflake generator
    ├── builder.py       # Dynamic builders for headers and payload structures
    ├── proxy.py         # Proxy formatting and ProxyScrape auto-tester
    ├── attachment.py    # GCS pre-signed upload handler
    └── client.py        # StealthDiscordClient orchestrator
```

## License

MIT License. See [LICENSE](LICENSE) for details.
