import re
import secrets
import time
import uuid
from curl_cffi import requests

try:
    from .constants import DEFAULT_BROWSER_IMPERSONATE, DEFAULT_USER_AGENT, DISCORD_BASE_URL, DISCORD_EPOCH
except ImportError:
    from constants import DEFAULT_BROWSER_IMPERSONATE, DEFAULT_USER_AGENT, DISCORD_BASE_URL, DISCORD_EPOCH


def generate_snowflake(timestamp_ms: int | None = None) -> str:
    """Generate ID Snowflake Discord berdasar timestamp milidetik."""
    current_time = timestamp_ms if timestamp_ms is not None else int(time.time() * 1000)
    return str((current_time - DISCORD_EPOCH) << 22)


def generate_installation_id() -> str:
    """Format: <Snowflake>.<Random27CharBase64>"""
    snowflake = generate_snowflake()
    random_hash = secrets.token_urlsafe(20).replace("-", "").replace("_", "")[:27]
    return f"{snowflake}.{random_hash}"


def scrape_client_build_number(
    user_agent: str = DEFAULT_USER_AGENT,
    impersonate: str = DEFAULT_BROWSER_IMPERSONATE,
    timeout: int = 10,
) -> int:
    """Scrape client_build_number terbaru langsung dari bundle JavaScript Discord."""
    url = f"{DISCORD_BASE_URL}/app"
    headers = {"User-Agent": user_agent}
    try:
        resp = requests.get(url, headers=headers, impersonate=impersonate, timeout=timeout)
        html = resp.text

        js_files = re.findall(r'<script\s+src="(/assets/[^"]+\.js)"', html)
        build_pattern = re.compile(r'buildNumber\s*:\s*"?(\d+)"?')

        for js_path in reversed(js_files):
            js_url = f"{DISCORD_BASE_URL}{js_path}"
            js_content = requests.get(js_url, headers=headers, impersonate=impersonate, timeout=timeout).text
            match = build_pattern.search(js_content)
            if match:
                return int(match.group(1))
    except Exception:
        pass

    # Fallback jika scraping asset Discord gagal
    return 637268


class DiscordSession:
    """
    Manajer sesi in-memory:
    Dibuat sekali saat proses pertama kali berjalan, lalu di-reuse terus menerus
    tanpa menyentuh disk (zero disk persistence).
    """

    _GLOBAL_STORE: dict = {}

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        build_number: int | None = None,
        force_new: bool = False,
    ):
        if force_new or not DiscordSession._GLOBAL_STORE:
            DiscordSession._GLOBAL_STORE = {
                "installation_id": generate_installation_id(),
                "client_launch_id": str(uuid.uuid4()),
                "launch_signature": str(uuid.uuid4()),
                "client_heartbeat_session_id": str(uuid.uuid4()),
                "build_number": build_number or scrape_client_build_number(user_agent),
            }

        data = DiscordSession._GLOBAL_STORE
        self.installation_id: str = data["installation_id"]
        self.client_launch_id: str = data["client_launch_id"]
        self.launch_signature: str = data["launch_signature"]
        self.client_heartbeat_session_id: str = data["client_heartbeat_session_id"]
        self.build_number: int = data["build_number"]

    @classmethod
    def reset(cls) -> None:
        """Reset seluruh state sesi in-memory."""
        cls._GLOBAL_STORE.clear()
