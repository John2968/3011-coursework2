import requests

from src.crawler import CrawlerError, QuotesCrawler


PAGE_ONE = """
<html>
  <head><title>Quotes page 1</title></head>
  <body>
    <div class="quote">
      <span class="text">"The world as we have created it."</span>
      <small class="author">Albert Einstein</small>
      <a class="tag">change</a>
      <a class="tag">world</a>
    </div>
    <li class="next"><a href="/page/2/">Next</a></li>
  </body>
</html>
"""


PAGE_TWO = """
<html>
  <head><title>Quotes page 2</title></head>
  <body>
    <div class="quote">
      <span class="text">"It is our choices that show what we truly are."</span>
      <small class="author">J. K. Rowling</small>
      <a class="tag">choices</a>
    </div>
  </body>
</html>
"""


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200) -> None:
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses: dict[str, FakeResponse]) -> None:
        self.responses = responses
        self.requested_urls: list[str] = []

    def get(self, url: str, timeout: float) -> FakeResponse:
        self.requested_urls.append(url)
        if url not in self.responses:
            raise requests.ConnectionError("unexpected url")
        return self.responses[url]


def test_crawl_follows_next_link_and_extracts_quote_text() -> None:
    session = FakeSession(
        {
            "https://quotes.toscrape.com/": FakeResponse(PAGE_ONE),
            "https://quotes.toscrape.com/page/2/": FakeResponse(PAGE_TWO),
        }
    )
    sleeps: list[float] = []
    crawler = QuotesCrawler(
        session=session,
        politeness_window=6,
        sleep_func=sleeps.append,
        clock=lambda: 100.0,
    )

    pages = crawler.crawl()

    assert [page.url for page in pages] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/page/2/",
    ]
    assert "Albert Einstein" in pages[0].text
    assert "choices" in pages[1].text
    assert sleeps == [6]


def test_crawl_uses_full_page_text_when_quote_blocks_are_missing() -> None:
    session = FakeSession({"https://quotes.toscrape.com/": FakeResponse("<h1>Hello</h1>")})
    crawler = QuotesCrawler(session=session, politeness_window=0)

    pages = crawler.crawl()

    assert len(pages) == 1
    assert pages[0].title == "Hello"
    assert pages[0].text == "Hello"


def test_crawl_stops_gracefully_after_request_failures() -> None:
    class BrokenSession:
        def get(self, url: str, timeout: float) -> FakeResponse:
            raise requests.Timeout("network is slow")

    crawler = QuotesCrawler(session=BrokenSession(), politeness_window=0, retries=1)

    assert crawler.crawl() == []


def test_crawler_rejects_invalid_configuration() -> None:
    try:
        QuotesCrawler(politeness_window=-1)
    except CrawlerError as exc:
        assert "politeness_window" in str(exc)
    else:
        raise AssertionError("Expected CrawlerError")

