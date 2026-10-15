import concurrent.futures
import re
from curl_cffi import requests

try:
    from .constants import DEFAULT_BROWSER_IMPERSONATE, DISCORD_API_BASE, PROXY_SCRAPE_V2_URL, PROXY_SCRAPE_V3_URL
except ImportError:
    from constants import DEFAULT_BROWSER_IMPERSONATE, DISCORD_API_BASE, PROXY_SCRAPE_V2_URL, PROXY_SCRAPE_V3_URL


class ProxyManager:
    """Utility untuk memvalidasi dan memformat string proxy universal."""

    @staticmethod
    def format_proxy(proxy: str) -> str:
        """
        Memastikan format proxy menyertakan skema protokol.
        Mendukung http://, https://, socks4://, socks5://, socks5h://.
        Default jika tanpa skema: socks5://
        """
        p = proxy.strip()
        if not re.match(r"^(http|https|socks4|socks5|socks5h)://", p, re.I):
            p = f"socks5://{p}"
        return p

    @staticmethod
    def test_proxy(
        proxy: str,
        test_url: str = f"{DISCORD_API_BASE}/experiments",
        impersonate: str = DEFAULT_BROWSER_IMPERSONATE,
        timeout: int = 4,
    ) -> bool:
        """Uji apakah proxy dapat terhubung ke endpoint target."""
        formatted = ProxyManager.format_proxy(proxy)
        try:
            r = requests.get(
                test_url,
                proxies={"all": formatted},
                impersonate=impersonate,
                timeout=timeout,
            )
            return r.status_code in (200, 401, 403, 404)
        except Exception:
            return False


class ProxyScrapeHandler:
    """
    Handler otomatis untuk mengambil dan memvalidasi proxy gratis dari ProxyScrape
    (https://proxyscrape.com/free-proxy-list).
    """

    @classmethod
    def fetch_proxies(
        cls,
        timeout: int = 10,
        impersonate: str = DEFAULT_BROWSER_IMPERSONATE,
    ) -> list[str]:
        """Ambil list proxy fresh langsung dari endpoint ProxyScrape API."""
        try:
            r = requests.get(PROXY_SCRAPE_V3_URL, impersonate=impersonate, timeout=timeout)
            if r.status_code == 200:
                lines = [l.strip() for l in r.text.splitlines() if l.strip() and not l.startswith("#")]
                if lines:
                    return lines
        except Exception:
            pass

        try:
            r = requests.get(PROXY_SCRAPE_V2_URL, impersonate=impersonate, timeout=timeout)
            if r.status_code == 200:
                lines = [l.strip() for l in r.text.splitlines() if l.strip()]
                return [f"socks5://{l}" for l in lines]
        except Exception:
            pass

        return []

    @classmethod
    def find_working_proxy(
        cls,
        max_candidates: int = 60,
        max_workers: int = 20,
        timeout: int = 4,
        verbose: bool = True,
    ) -> str | None:
        """
        Fetch proxy dari ProxyScrape dan uji paralel ke Discord endpoint
        untuk mendapatkan 1 proxy yang hidup dan responsif.
        """
        if verbose:
            print("[*] Mengambil proxy fresh dari ProxyScrape...")
        proxies = cls.fetch_proxies()
        if not proxies:
            if verbose:
                print("[!] Gagal mengambil proxy dari ProxyScrape.")
            return None

        if verbose:
            print(f"[*] Mendapatkan {len(proxies)} kandidat proxy. Memvalidasi ke server Discord...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            candidates = proxies[:max_candidates]
            futures = [
                executor.submit(ProxyManager.test_proxy, p, f"{DISCORD_API_BASE}/experiments", DEFAULT_BROWSER_IMPERSONATE, timeout)
                for p in candidates
            ]
            for future, proxy_str in zip(futures, candidates):
                if future.result():
                    executor.shutdown(wait=False, cancel_futures=True)
                    if verbose:
                        print(f"[*] Proxy valid ditemukan dari ProxyScrape: {proxy_str}")
                    return proxy_str

        if verbose:
            print("[!] Tidak ada proxy yang lolos uji dari batch pertama.")
        return None
