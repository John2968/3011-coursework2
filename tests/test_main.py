from pathlib import Path

from src.main import SearchTool
from src.models import CrawledPage


class StubCrawler:
    def crawl(self) -> list[CrawledPage]:
        return [
            CrawledPage(
                url="https://quotes.toscrape.com/",
                title="Quotes",
                text="good friends share good ideas",
            )
        ]


class EmptyCrawler:
    def crawl(self) -> list[CrawledPage]:
        return []


def test_build_load_print_and_find_commands(tmp_path: Path) -> None:
    index_path = tmp_path / "index.json"
    tool = SearchTool(index_path=index_path, crawler=StubCrawler())

    build_output = tool.execute("build")
    assert "Built index from 1 page(s)." in build_output
    assert index_path.exists()

    load_output = tool.execute("load")
    assert load_output[0].startswith("Loaded index")

    print_output = tool.execute("print good")
    assert print_output[0] == "Term: good"

    find_output = tool.execute("find good friends")
    assert find_output[0] == "Results for: good friends"


def test_command_handler_reports_invalid_or_unready_states(tmp_path: Path) -> None:
    tool = SearchTool(index_path=tmp_path / "missing.json", crawler=EmptyCrawler())

    assert tool.execute("")[0].startswith("Please enter")
    assert tool.execute("unknown")[0].startswith("Unknown command")
    assert tool.execute("print")[0] == "Usage: print <word>"
    assert tool.execute("find")[0] == "Usage: find <word or phrase>"
    assert "No index loaded" in tool.execute("print good")[0]
    assert "Run 'build'" in tool.execute("load")[0]
    assert tool.execute("build")[0].startswith("No pages were crawled")
    assert "Available commands" in tool.execute("help")[0]
    assert tool.execute("exit") == ["Goodbye."]

