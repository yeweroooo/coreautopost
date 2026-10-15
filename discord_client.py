"""
Entrypoint & backward compatibility layer for discord_stealth.
Seluruh logika inti dan builder telah direfactor secara modular di package `discord_stealth`.
"""

from discord_stealth import (
    DEFAULT_BROWSER_IMPERSONATE,
    DEFAULT_LOCALE,
    DEFAULT_TIMEZONE,
    DEFAULT_USER_AGENT,
    DISCORD_API_BASE,
    DISCORD_BASE_URL,
    DISCORD_EPOCH,
    AttachmentUploader,
    DiscordSession,
    HeaderBuilder,
    PayloadBuilder,
    ProxyManager,
    ProxyScrapeHandler,
    StealthDiscordClient,
    generate_installation_id,
    generate_snowflake,
    scrape_client_build_number,
)

# Alias backward compatibility
get_discord_build_number = scrape_client_build_number

__all__ = [
    "StealthDiscordClient",
    "DiscordSession",
    "generate_snowflake",
    "generate_installation_id",
    "get_discord_build_number",
    "scrape_client_build_number",
    "HeaderBuilder",
    "PayloadBuilder",
    "ProxyManager",
    "ProxyScrapeHandler",
    "AttachmentUploader",
    "DISCORD_EPOCH",
    "DISCORD_BASE_URL",
    "DISCORD_API_BASE",
    "DEFAULT_USER_AGENT",
    "DEFAULT_BROWSER_IMPERSONATE",
    "DEFAULT_LOCALE",
    "DEFAULT_TIMEZONE",
]
