import base64
import json
import re

try:
    from .constants import DEFAULT_LOCALE, DEFAULT_TIMEZONE, DISCORD_BASE_URL
    from .session import DiscordSession, generate_snowflake
except ImportError:
    from constants import DEFAULT_LOCALE, DEFAULT_TIMEZONE, DISCORD_BASE_URL
    from session import DiscordSession, generate_snowflake


class SuperPropertiesBuilder:
    """Builder dinamis untuk header X-Super-Properties Discord."""

    @staticmethod
    def parse_user_agent(user_agent: str) -> tuple[str, str, str]:
        """Ekstrak (os, browser, browser_version) dari User-Agent string."""
        os_name = "Linux"
        if "Windows" in user_agent:
            os_name = "Windows"
        elif "Macintosh" in user_agent or "Mac OS X" in user_agent:
            os_name = "Mac OS X"

        browser = "Firefox"
        version = "153.0"

        if "Firefox/" in user_agent:
            browser = "Firefox"
            m = re.search(r"Firefox/([0-9.]+)", user_agent)
            if m:
                version = m.group(1)
        elif "Chrome/" in user_agent:
            browser = "Chrome"
            m = re.search(r"Chrome/([0-9.]+)", user_agent)
            if m:
                version = m.group(1)

        return os_name, browser, version

    @classmethod
    def build(
        cls,
        session: DiscordSession,
        user_agent: str,
        locale: str = DEFAULT_LOCALE,
    ) -> str:
        """Membuat base64 compact JSON X-Super-Properties secara dinamis."""
        os_name, browser, version = cls.parse_user_agent(user_agent)

        properties = {
            "os": os_name,
            "browser": browser,
            "device": "",
            "device_model_name": "",
            "system_locale": locale,
            "has_client_mods": False,
            "browser_user_agent": user_agent,
            "browser_version": version,
            "os_version": "",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": session.build_number,
            "client_event_source": None,
            "client_launch_id": session.client_launch_id,
            "launch_signature": session.launch_signature,
            "client_heartbeat_session_id": session.client_heartbeat_session_id,
            "client_app_state": "focused",
        }

        compact_json = json.dumps(properties, separators=(",", ":"))
        return base64.b64encode(compact_json.encode("utf-8")).decode("utf-8")


class HeaderBuilder:
    """Builder dinamis untuk menyusun seluruh HTTP headers 1:1 identik dengan Firefox."""

    @staticmethod
    def build_context_properties(location: str = "chat_input") -> str:
        data = {"location": location}
        return base64.b64encode(json.dumps(data, separators=(",", ":")).encode("utf-8")).decode("utf-8")

    @classmethod
    def build_request_headers(
        cls,
        token: str,
        guild_id: str,
        channel_id: str,
        session: DiscordSession,
        user_agent: str,
        locale: str = DEFAULT_LOCALE,
        timezone: str = DEFAULT_TIMEZONE,
        cookie_string: str | None = None,
        context_location: str = "chat_input",
    ) -> dict[str, str]:
        super_props_b64 = SuperPropertiesBuilder.build(session, user_agent, locale)
        context_props_b64 = cls.build_context_properties(context_location)

        headers = {
            "Host": "discord.com",
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Language": f"{locale},en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "Authorization": token,
            "X-Context-Properties": context_props_b64,
            "X-Super-Properties": super_props_b64,
            "X-Installation-ID": session.installation_id,
            "X-Discord-Locale": locale,
            "X-Discord-Timezone": timezone,
            "X-Debug-Options": "bugReporterEnabled",
            "Origin": DISCORD_BASE_URL,
            "Alt-Used": "discord.com",
            "Connection": "keep-alive",
            "Referer": f"{DISCORD_BASE_URL}/channels/{guild_id}/{channel_id}",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0",
        }

        if cookie_string:
            headers["Cookie"] = cookie_string

        return headers


class PayloadBuilder:
    """Builder dinamis untuk JSON payload pengiriman pesan Discord."""

    @staticmethod
    def build_message_payload(
        content: str = "",
        nonce: str | None = None,
        attachments: list[dict] | None = None,
        tts: bool = False,
        flags: int = 0,
        mobile_network_type: str = "unknown",
    ) -> dict:
        payload = {
            "mobile_network_type": mobile_network_type,
            "content": content,
            "nonce": nonce or generate_snowflake(),
            "tts": tts,
            "flags": flags,
        }

        if attachments:
            payload["attachments"] = attachments

        return payload
