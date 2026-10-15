DISCORD_EPOCH: int = 1420070400000

DISCORD_BASE_URL: str = "https://discord.com"
DISCORD_API_BASE: str = "https://discord.com/api/v9"

DEFAULT_USER_AGENT: str = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0"
)
DEFAULT_BROWSER_IMPERSONATE: str = "firefox135"
DEFAULT_LOCALE: str = "en-US"
DEFAULT_TIMEZONE: str = "Asia/Jakarta"

PROXY_SCRAPE_V3_URL: str = (
    "https://api.proxyscrape.com/v3/free-proxy-list/get"
    "?request=displayproxies&protocol=http,socks4,socks5&proxy_format=protocolipport&format=text"
)
PROXY_SCRAPE_V2_URL: str = (
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=all&timeout=5000&country=all&ssl=all&anonymity=all"
)
