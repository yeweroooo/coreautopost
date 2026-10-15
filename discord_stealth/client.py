import random
import time
from curl_cffi import requests

from .attachment import AttachmentUploader
from .builder import HeaderBuilder, PayloadBuilder
from .constants import (
    DEFAULT_BROWSER_IMPERSONATE,
    DEFAULT_LOCALE,
    DEFAULT_TIMEZONE,
    DEFAULT_USER_AGENT,
    DISCORD_API_BASE,
)
from .proxy import ProxyManager, ProxyScrapeHandler
from .session import DiscordSession


class StealthDiscordClient:
    """
    Stealth Headless Client modular untuk Discord REST API.
    Bebas hardcoded/static payload dan tanpa disk persistence.
    """

    def __init__(
        self,
        token: str,
        user_agent: str = DEFAULT_USER_AGENT,
        impersonate: str = DEFAULT_BROWSER_IMPERSONATE,
        locale: str = DEFAULT_LOCALE,
        timezone: str = DEFAULT_TIMEZONE,
        proxy: str | None = None,
        cookie_string: str | None = None,
        build_number: int | None = None,
        force_new_session: bool = False,
    ):
        self.token = token
        self.user_agent = user_agent
        self.impersonate = impersonate
        self.locale = locale
        self.timezone = timezone
        self.cookie_string = cookie_string

        self.proxy: str | None = None
        if proxy in ("auto", "proxyscrape"):
            self.proxy = ProxyScrapeHandler.find_working_proxy()
        elif proxy:
            self.proxy = ProxyManager.format_proxy(proxy)

        self.session = DiscordSession(
            user_agent=self.user_agent,
            build_number=build_number,
            force_new=force_new_session,
        )

        proxies_dict = {"all": self.proxy} if self.proxy else None
        self.http = requests.Session(impersonate=self.impersonate, proxies=proxies_dict)

    def set_proxy(self, proxy: str | None) -> None:
        """Ubah atau pasang proxy baru secara dinamis."""
        if proxy in ("auto", "proxyscrape"):
            self.proxy = ProxyScrapeHandler.find_working_proxy()
        elif proxy:
            self.proxy = ProxyManager.format_proxy(proxy)
        else:
            self.proxy = None

        self.http.proxies = {"all": self.proxy} if self.proxy else None

    def rotate_proxyscrape_proxy(self) -> str | None:
        """Fetch proxy baru yang aktif dari ProxyScrape dan terapkan ke klien."""
        new_proxy = ProxyScrapeHandler.find_working_proxy()
        if new_proxy:
            self.set_proxy(new_proxy)
        return new_proxy

    @classmethod
    def reset_session(cls) -> None:
        """Reset sesi global in-memory."""
        DiscordSession.reset()

    def get_headers(self, guild_id: str, channel_id: str) -> dict[str, str]:
        """Menyusun full header permintaan secara dinamis."""
        return HeaderBuilder.build_request_headers(
            token=self.token,
            guild_id=guild_id,
            channel_id=channel_id,
            session=self.session,
            user_agent=self.user_agent,
            locale=self.locale,
            timezone=self.timezone,
            cookie_string=self.cookie_string,
        )

    def trigger_typing(self, guild_id: str, channel_id: str, timeout: int = 5) -> bool:
        """Memicu indikator 'sedang mengetik...' ke channel Discord."""
        url = f"{DISCORD_API_BASE}/channels/{channel_id}/typing"
        headers = self.get_headers(guild_id, channel_id)
        try:
            resp = self.http.post(url, headers=headers, timeout=timeout)
            return resp.status_code == 204
        except Exception:
            return False

    def send_message(
        self,
        guild_id: str,
        channel_id: str,
        content: str = "",
        files: list[str | tuple[str, bytes, str | None]] | None = None,
        simulate_typing: bool = True,
        typing_delay_range: tuple[float, float] = (0.6, 1.4),
        timeout: int = 15,
    ) -> tuple[int, str]:
        """
        Kirim pesan stealth ke channel Discord (mendukung teks dan file attachment).
        """
        headers = self.get_headers(guild_id, channel_id)
        attachments_payload = []
        if files:
            attachments_payload = AttachmentUploader.upload_files(
                http_session=self.http,
                channel_id=channel_id,
                request_headers=headers,
                user_agent=self.user_agent,
                files=files,
                timeout=timeout * 2,
            )

        if simulate_typing:
            self.trigger_typing(guild_id, channel_id)
            delay = random.uniform(typing_delay_range[0], typing_delay_range[1])
            time.sleep(delay)

        payload = PayloadBuilder.build_message_payload(
            content=content,
            attachments=attachments_payload if attachments_payload else None,
        )

        url = f"{DISCORD_API_BASE}/channels/{channel_id}/messages"
        resp = self.http.post(url, headers=headers, json=payload, timeout=timeout)
        return resp.status_code, resp.text
