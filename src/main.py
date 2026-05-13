"""Command-line interface for the coursework search tool."""

from __future__ import annotations

import argparse
import shlex
from pathlib import Path

from .crawler import QuotesCrawler
from .indexer import InvertedIndexBuilder
from .search import SearchEngine
from .storage import DEFAULT_INDEX_PATH, IndexStorageError, load_index, save_index


class SearchTool:
    """Stateful command handler used by both the interactive shell and tests."""

    def __init__(
        self,
        *,
        index_path: Path | str = DEFAULT_INDEX_PATH,
        crawler: QuotesCrawler | None = None,
        builder: InvertedIndexBuilder | None = None,
        engine: SearchEngine | None = None,
    ) -> None:
        self.index_path = Path(index_path)
        self.crawler = crawler or QuotesCrawler()
        self.builder = builder or InvertedIndexBuilder()
        self.engine = engine or SearchEngine()

    def execute(self, command_line: str) -> list[str]:
        command_line = command_line.strip()
        if not command_line:
            return ["Please enter a command. Type 'help' for available commands."]

        try:
            parts = shlex.split(command_line)
        except ValueError as exc:
            return [f"Could not parse command: {exc}"]

        command = parts[0].lower()
        arguments = parts[1:]

        if command == "build":
            return self._build()
        if command == "load":
            return self._load()
        if command == "print":
            return self._print(arguments)
        if command == "find":
            return self._find(arguments)
        if command == "help":
            return self._help()
        if command in {"exit", "quit"}:
            return ["Goodbye."]
        return [f"Unknown command '{command}'. Type 'help' for available commands."]

    def _build(self) -> list[str]:
        pages = self.crawler.crawl()
        if not pages:
            return ["No pages were crawled. Check your network connection and try again."]

        index = self.builder.build(pages)
        save_index(index, self.index_path)
        self.engine.load(index)
        return [
            f"Built index from {index.document_count} page(s).",
            f"Indexed {len(index.terms)} unique term(s).",
            f"Saved index to {self.index_path}.",
        ]

    def _load(self) -> list[str]:
        try:
            index = load_index(self.index_path)
        except IndexStorageError as exc:
            return [str(exc)]
        self.engine.load(index)
        return [
            f"Loaded index from {self.index_path}.",
            f"{index.document_count} page(s), {len(index.terms)} unique term(s).",
        ]

    def _print(self, arguments: list[str]) -> list[str]:
        if not arguments:
            return ["Usage: print <word>"]
        try:
            return self.engine.explain_term(arguments[0])
        except ValueError as exc:
            return [str(exc)]

    def _find(self, arguments: list[str]) -> list[str]:
        if not arguments:
            return ["Usage: find <word or phrase>"]
        try:
            return self.engine.format_results(" ".join(arguments))
        except ValueError as exc:
            return [str(exc)]

    @staticmethod
    def _help() -> list[str]:
        return [
            "Available commands:",
            "  build              Crawl the target site, build the index, and save it.",
            "  load               Load the saved index from disk.",
            "  print <word>       Print postings for a word.",
            "  find <query...>    Find pages containing all query terms.",
            "  help               Show this help message.",
            "  exit               Exit the shell.",
        ]


def run_shell(tool: SearchTool) -> None:
    print("COMP3011 Search Engine Tool. Type 'help' for commands.")
    while True:
        try:
            command_line = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        output = tool.execute(command_line)
        for line in output:
            print(line)
        if command_line.strip().lower() in {"exit", "quit"}:
            break


def main() -> None:
    parser = argparse.ArgumentParser(description="COMP3011 Search Engine Tool")
    parser.add_argument(
        "--index-path",
        default=str(DEFAULT_INDEX_PATH),
        help="Path to the compiled index file.",
    )
    args = parser.parse_args()
    run_shell(SearchTool(index_path=args.index_path))


if __name__ == "__main__":
    main()

