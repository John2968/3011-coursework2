"""Shared data models for crawling, indexing, and searching."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class CrawledPage:
    """A page discovered by the crawler and ready to be indexed."""

    url: str
    title: str
    text: str


@dataclass
class Document:
    """Metadata stored for each indexed page."""

    doc_id: str
    url: str
    title: str
    preview: str
    token_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "url": self.url,
            "title": self.title,
            "preview": self.preview,
            "token_count": self.token_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        return cls(
            doc_id=str(data["doc_id"]),
            url=str(data["url"]),
            title=str(data.get("title", "")),
            preview=str(data.get("preview", "")),
            token_count=int(data.get("token_count", 0)),
        )


@dataclass
class Posting:
    """A term's statistics within one document."""

    doc_id: str
    frequency: int = 0
    positions: list[int] = field(default_factory=list)

    def add_position(self, position: int) -> None:
        self.frequency += 1
        self.positions.append(position)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "frequency": self.frequency,
            "positions": self.positions,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Posting":
        return cls(
            doc_id=str(data["doc_id"]),
            frequency=int(data.get("frequency", 0)),
            positions=[int(position) for position in data.get("positions", [])],
        )


@dataclass
class TermEntry:
    """All postings for a single indexed term."""

    doc_freq: int = 0
    postings: dict[str, Posting] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_freq": self.doc_freq,
            "postings": {
                doc_id: posting.to_dict()
                for doc_id, posting in sorted(self.postings.items())
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TermEntry":
        postings = {
            str(doc_id): Posting.from_dict(posting_data)
            for doc_id, posting_data in data.get("postings", {}).items()
        }
        return cls(doc_freq=int(data.get("doc_freq", len(postings))), postings=postings)


@dataclass
class InvertedIndex:
    """Complete inverted index plus document and build metadata."""

    documents: dict[str, Document] = field(default_factory=dict)
    terms: dict[str, TermEntry] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def document_count(self) -> int:
        return len(self.documents)

    @property
    def average_document_length(self) -> float:
        if not self.documents:
            return 0.0
        total_tokens = sum(document.token_count for document in self.documents.values())
        return total_tokens / len(self.documents)

    def to_dict(self) -> dict[str, Any]:
        metadata = {"schema_version": SCHEMA_VERSION, **self.metadata}
        metadata["document_count"] = self.document_count
        metadata["average_document_length"] = self.average_document_length
        return {
            "metadata": metadata,
            "documents": {
                doc_id: document.to_dict()
                for doc_id, document in sorted(self.documents.items())
            },
            "terms": {
                term: entry.to_dict()
                for term, entry in sorted(self.terms.items())
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InvertedIndex":
        metadata = dict(data.get("metadata", {}))
        documents = {
            str(doc_id): Document.from_dict(document_data)
            for doc_id, document_data in data.get("documents", {}).items()
        }
        terms = {
            str(term): TermEntry.from_dict(term_data)
            for term, term_data in data.get("terms", {}).items()
        }
        return cls(documents=documents, terms=terms, metadata=metadata)


@dataclass(frozen=True)
class SearchResult:
    """A ranked search result returned by the query engine."""

    document: Document
    score: float
    matched_terms: tuple[str, ...]
    term_frequencies: dict[str, int]

