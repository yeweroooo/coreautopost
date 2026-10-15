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

## License

MIT License. See [LICENSE](LICENSE) for details.
