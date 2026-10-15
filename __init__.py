try:
    from .attachment import AttachmentUploader
    from .builder import HeaderBuilder, PayloadBuilder, SuperPropertiesBuilder
    from .client import StealthDiscordClient
    from .constants import (
        DEFAULT_BROWSER_IMPERSONATE,
        DEFAULT_LOCALE,
        DEFAULT_TIMEZONE,
        DEFAULT_USER_AGENT,
        DISCORD_API_BASE,
        DISCORD_BASE_URL,
        DISCORD_EPOCH,
    )
    from .proxy import ProxyManager, ProxyScrapeHandler
    from .session import (
        DiscordSession,
        generate_installation_id,
        generate_snowflake,
        scrape_client_build_number,
    )
except ImportError:
    from attachment import AttachmentUploader
    from builder import HeaderBuilder, PayloadBuilder, SuperPropertiesBuilder
    from client import StealthDiscordClient
    from constants import (
        DEFAULT_BROWSER_IMPERSONATE,
        DEFAULT_LOCALE,
        DEFAULT_TIMEZONE,
        DEFAULT_USER_AGENT,
        DISCORD_API_BASE,
        DISCORD_BASE_URL,
        DISCORD_EPOCH,
    )
    from proxy import ProxyManager, ProxyScrapeHandler
    from session import (
        DiscordSession,
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
    "SuperPropertiesBuilder",
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
