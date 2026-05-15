"""Query processing over the inverted index."""

from __future__ import annotations

import math
from collections import Counter

from .indexer import tokenize
from .models import InvertedIndex, Posting, SearchResult


class SearchEngine:
    """Searches an inverted index with AND semantics and BM25-style ranking."""

    def __init__(self, index: InvertedIndex | None = None) -> None:
        self.index = index

    def load(self, index: InvertedIndex) -> None:
        self.index = index

    def require_index(self) -> InvertedIndex:
        if self.index is None:
            raise ValueError("No index loaded. Run 'build' or 'load' first.")
        return self.index

    def normalise_query(self, query: str) -> list[str]:
        """Tokenise a user query and remove duplicate terms while preserving order."""

        terms = tokenize(query)
        return list(dict.fromkeys(terms))

    def postings_for(self, term: str) -> dict[str, Posting]:
        index = self.require_index()
        tokens = tokenize(term)
        if not tokens:
            return {}
        entry = index.terms.get(tokens[0])
        return entry.postings if entry else {}

    def find(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        index = self.require_index()
        terms = self.normalise_query(query)
        if not terms:
            return []

        posting_sets: list[set[str]] = []
        for term in terms:
            entry = index.terms.get(term)
            if entry is None:
                return []
            posting_sets.append(set(entry.postings))

        # AND search: only documents appearing in every posting list can match.
        matching_doc_ids = set.intersection(*posting_sets) if posting_sets else set()
        results = [
            SearchResult(
                document=index.documents[doc_id],
                score=self._bm25_score(index, doc_id, terms),
                matched_terms=tuple(terms),
                term_frequencies={
                    term: index.terms[term].postings[doc_id].frequency for term in terms
                },
            )
            for doc_id in matching_doc_ids
        ]
        return sorted(results, key=lambda result: (-result.score, result.document.url))[:limit]

    def explain_term(self, term: str) -> list[str]:
        index = self.require_index()
        tokens = tokenize(term)
        if not tokens:
            return ["Please provide a word to print."]

        normalised_term = tokens[0]
        entry = index.terms.get(normalised_term)
        if entry is None:
            return [f"No entries found for '{normalised_term}'."]

        lines = [
            f"Term: {normalised_term}",
            f"Document frequency: {entry.doc_freq}",
        ]
        for doc_id, posting in sorted(
            entry.postings.items(),
            key=lambda item: (-item[1].frequency, index.documents[item[0]].url),
        ):
            document = index.documents[doc_id]
            positions = ", ".join(str(position) for position in posting.positions[:12])
            if len(posting.positions) > 12:
                positions += ", ..."
            lines.append(
                f"- {document.url} | freq={posting.frequency} | positions=[{positions}]"
            )
        return lines

    def format_results(self, query: str, *, limit: int = 10) -> list[str]:
        terms = self.normalise_query(query)
        if not terms:
            return ["Please provide at least one search term."]

        results = self.find(query, limit=limit)
        if not results:
            return [f"No pages found containing all terms: {' '.join(terms)}"]

        lines = [f"Results for: {' '.join(terms)}"]
        for rank, result in enumerate(results, start=1):
            frequencies = ", ".join(
                f"{term}={frequency}"
                for term, frequency in sorted(result.term_frequencies.items())
            )
            lines.extend(
                [
                    f"{rank}. {result.document.url}",
                    f"   score={result.score:.4f} | {frequencies}",
                    f"   {result.document.preview}",
                ]
            )
        return lines

    @staticmethod
    def _bm25_score(
        index: InvertedIndex,
        doc_id: str,
        terms: list[str],
        *,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> float:
        if index.document_count == 0:
            return 0.0

        query_counts = Counter(terms)
        document = index.documents[doc_id]
        avg_doc_len = index.average_document_length or 1.0
        score = 0.0

        for term, query_frequency in query_counts.items():
            entry = index.terms[term]
            posting = entry.postings[doc_id]
            # BM25-style IDF reduces the impact of words that appear in many pages.
            idf = math.log(
                1
                + (index.document_count - entry.doc_freq + 0.5)
                / (entry.doc_freq + 0.5)
            )
            denominator = posting.frequency + k1 * (
                1 - b + b * (document.token_count / avg_doc_len)
            )
            score += query_frequency * idf * (
                posting.frequency * (k1 + 1) / denominator
            )

        return score

