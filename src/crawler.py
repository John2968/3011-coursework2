"""Polite crawler for https://quotes.toscrape.com/."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests import Session

from .models import CrawledPage


LOGGER = logging.getLogger(__name__)
DEFAULT_BASE_URL = "https://quotes.toscrape.com/"


class CrawlerError(RuntimeError):
    """Raised when crawler configuration is invalid."""


class QuotesCrawler:
    """Crawl quote listing pages while respecting a politeness window."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        *,
        politeness_window: float = 6.0,
        timeout: float = 10.0,
        retries: int = 2,
        session: Session | None = None,
        sleep_func: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if politeness_window < 0:
            raise CrawlerError("politeness_window must be non-negative")
        if retries < 0:
            raise CrawlerError("retries must be non-negative")

        self.base_url = base_url
        self.politeness_window = politeness_window
        self.timeout = timeout
        self.retries = retries
        self.session = session or requests.Session()
        self.sleep_func = sleep_func
        self.clock = clock
        self._last_request_at: float | None = None
        self._base_domain = urlparse(base_url).netloc

    def crawl(self, max_pages: int | None = None) -> list[CrawledPage]:
        """Crawl paginated quote pages until no in-site next page is found."""

        pages: list[CrawledPage] = []
        visited: set[str] = set()
        next_url: str | None = self.base_url

        while next_url and next_url not in visited:
            if max_pages is not None and len(pages) >= max_pages:
                break

            visited.add(next_url)
            html = self._fetch(next_url)
            if html is None:
                break

            page, discovered_next = self._parse_page(next_url, html)
            pages.append(page)
            next_url = discovered_next if self._is_allowed_url(discovered_next) else None

        return pages

    def _fetch(self, url: str) -> str | None:
        for attempt in range(self.retries + 1):
            self._respect_politeness()
            try:
                response = self.session.get(url, timeout=self.timeout)
                self._last_request_at = self.clock()
                response.raise_for_status()
                return response.text
            except requests.RequestException as exc:
                self._last_request_at = self.clock()
                LOGGER.warning("Request failed for %s on attempt %s: %s", url, attempt + 1, exc)
                if attempt >= self.retries:
                    return None
        return None

    def _respect_politeness(self) -> None:
        if self._last_request_at is None or self.politeness_window == 0:
            return
        elapsed = self.clock() - self._last_request_at
        remaining = self.politeness_window - elapsed
        if remaining > 0:
            self.sleep_func(remaining)

    def _parse_page(self, url: str, html: str) -> tuple[CrawledPage, str | None]:
        soup = BeautifulSoup(html, "html.parser")
        title = self._extract_title(soup, url)
        text_parts = self._extract_quote_text(soup)

        if not text_parts:
            text_parts = [soup.get_text(" ", strip=True)]

        next_url = self._extract_next_url(soup, url)
        return CrawledPage(url=url, title=title, text=" ".join(text_parts)), next_url

    @staticmethod
    def _extract_title(soup: BeautifulSoup, fallback: str) -> str:
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        heading = soup.find(["h1", "h2"])
        if heading:
            return heading.get_text(" ", strip=True)
        return fallback

    @staticmethod
    def _extract_quote_text(soup: BeautifulSoup) -> list[str]:
        text_parts: list[str] = []
        for quote in soup.select(".quote"):
            quote_text = quote.select_one(".text")
            author = quote.select_one(".author")
            tags = [tag.get_text(" ", strip=True) for tag in quote.select(".tag")]
            block_parts = [
                quote_text.get_text(" ", strip=True) if quote_text else "",
                author.get_text(" ", strip=True) if author else "",
                " ".join(tags),
            ]
            text_parts.append(" ".join(part for part in block_parts if part))
        return text_parts

    @staticmethod
    def _extract_next_url(soup: BeautifulSoup, current_url: str) -> str | None:
        next_link = soup.select_one("li.next a")
        if next_link is None:
            for link in soup.find_all("a"):
                if link.get_text(" ", strip=True).lower() == "next":
                    next_link = link
                    break

        href = next_link.get("href") if next_link else None
        if not href:
            return None
        return urljoin(current_url, href)

    def _is_allowed_url(self, url: str | None) -> bool:
        return bool(url) and urlparse(url).netloc == self._base_domain

