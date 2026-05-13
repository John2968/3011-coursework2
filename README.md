# COMP3011 Coursework 2: Search Engine Tool

This repository contains a Python command-line search tool for
[`https://quotes.toscrape.com/`](https://quotes.toscrape.com/). The program
crawls the target website, builds an inverted index with word-level statistics,
saves the compiled index as JSON, and supports interactive search commands over
the saved data.

The implementation is designed for COMP3011 Coursework 2 and focuses on the
required search engine workflow: crawling, indexing, persistent storage, query
processing, testing, and clear documentation of design decisions.

## Features

- Crawls the paginated quote pages from `quotes.toscrape.com`.
- Enforces a default 6 second politeness window between HTTP requests.
- Parses quote text, authors, and tags with Beautiful Soup.
- Falls back to page-level text extraction if expected quote elements are not
  present.
- Builds a case-insensitive inverted index.
- Stores document frequency, term frequency, word positions, document length,
  URL, title, and preview text.
- Saves and loads the compiled index from `data/index.json`.
- Supports the required `build`, `load`, `print`, and `find` commands.
- Handles empty queries, missing words, missing index files, malformed commands,
  and network request failures gracefully.
- Ranks matching pages with a BM25-style score for multi-word search results.
- Includes automated unit, integration, CLI, and performance tests.

## Project Structure

```text
coursework2/
  src/
    __init__.py
    crawler.py
    indexer.py
    main.py
    models.py
    search.py
    storage.py
  tests/
    test_crawler.py
    test_indexer.py
    test_main.py
    test_performance.py
    test_search.py
    test_storage.py
  data/
    index.json
  requirements.txt
  pyproject.toml
  README.md
  VIDEO_SCRIPT.md
```

## Installation

Python 3.12 was used during development and testing.

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Alternatively, install the dependencies directly into the active Python
environment:

```powershell
python -m pip install -r requirements.txt
```

The runtime dependencies are `requests` and `beautifulsoup4`. The test
dependencies are `pytest` and `pytest-cov`.

## Running the Search Tool

Start the interactive command-line interface from the repository root:

```powershell
python -m src.main
```

The prompt accepts the following commands:

```text
> build
> load
> print nonsense
> find indifference
> find good friends
> help
> exit
```

The index path can be changed with:

```powershell
python -m src.main --index-path data/index.json
```

## Command Behaviour

`build` crawls the target website, constructs the inverted index, saves it to
`data/index.json`, and loads the new index into memory. A live build is expected
to take time because the crawler waits at least 6 seconds between successive
requests.

Example successful build output:

```text
Built index from 10 page(s).
Indexed 849 unique term(s).
Saved index to data\index.json.
```

`load` reads the saved index from disk and makes it available for `print` and
`find` without crawling the website again.

Example:

```text
> load
Loaded index from data\index.json.
10 page(s), 849 unique term(s).
```

`print <word>` displays the posting list for one normalised term. The output
includes document frequency, page URL, term frequency in each page, and token
positions.

Example:

```text
> print nonsense
Term: nonsense
Document frequency: 1
- https://quotes.toscrape.com/page/6/ | freq=1 | positions=[...]
```

`find <query...>` searches for pages containing all query terms. Query matching
is case-insensitive. Results are ranked by relevance and include a score,
per-term frequencies, URL, and document preview.

Example:

```text
> find good friends
Results for: good friends
1. https://quotes.toscrape.com/page/1/
   score=...
   ...
```

## Architecture

The implementation separates crawling, indexing, persistence, query processing,
and the user interface into independent modules.

```text
main.py
  - interactive command shell
  - command parsing and user-facing messages

crawler.py
  - polite HTTP requests
  - pagination discovery
  - HTML parsing and fallback extraction

indexer.py
  - tokenisation and normalisation
  - inverted index construction
  - term frequency and position recording

storage.py
  - JSON save/load
  - schema version validation
  - readable storage format for submission

search.py
  - posting list lookup
  - multi-term AND matching
  - BM25-style ranking
  - formatted result output

models.py
  - dataclasses for crawled pages, documents, postings, index entries, and
    search results
```

## Inverted Index Design

The compiled index is stored in JSON so that it can be submitted and inspected
directly. The main sections are:

- `metadata`: schema version, source site, creation timestamp, document count,
  and average document length.
- `documents`: document ID to URL, title, preview, and token count.
- `terms`: normalised term to document frequency and posting list.
- `postings`: document-specific frequency and word positions for a term.

A simplified structure is:

```json
{
  "metadata": {
    "schema_version": "1.0",
    "source_site": "https://quotes.toscrape.com/",
    "document_count": 10
  },
  "documents": {
    "doc_id": {
      "url": "https://quotes.toscrape.com/",
      "title": "Quotes to Scrape",
      "preview": "...",
      "token_count": 123
    }
  },
  "terms": {
    "good": {
      "doc_freq": 3,
      "postings": {
        "doc_id": {
          "frequency": 2,
          "positions": [15, 42]
        }
      }
    }
  }
}
```

This design gives direct lookup for `print <word>` and efficient multi-word
search by intersecting posting-list document IDs. Storing positions makes the
index more informative than a simple word-to-page mapping and supports clear
explanation of how each word appears in each page.

## Search Strategy

Input text is normalised by lowercasing and tokenising alphanumeric words. This
makes searches case-insensitive, so `Good`, `good`, and `GOOD` are treated as
the same term.

Multi-word queries use AND semantics: a page is returned only when it contains
all query terms. Matching pages are ranked with a BM25-style score based on term
frequency, document frequency, document length, and average document length.
This improves result ordering while keeping the ranking formula compact enough
to explain in the video demonstration.

## Error Handling

The crawler catches request exceptions and stops gracefully if repeated attempts
fail. The command-line interface returns user-readable messages for invalid
commands, empty queries, missing command arguments, unloaded indexes, and
missing or invalid index files.

Examples:

```text
> find
Usage: find <word or phrase>

> print
Usage: print <word>

> find wordthatdoesnotexist
No pages found containing all terms: wordthatdoesnotexist
```

## Testing

The test suite can be run with:

```powershell
python -m pytest
```

The local test result after implementation was:

```text
19 passed
TOTAL coverage: 90%
```

Test coverage is above the 85% target stated in the very good grade band. The
tests focus on meaningful behaviour rather than only increasing line coverage.

Test areas:

- `tests/test_crawler.py`: pagination, quote extraction, fallback text parsing,
  request failure handling, and crawler configuration validation.
- `tests/test_indexer.py`: tokenisation, case-insensitivity, document metadata,
  frequency counts, positions, and empty page handling.
- `tests/test_storage.py`: JSON save/load round trips, missing files, invalid
  JSON, and schema version checks.
- `tests/test_search.py`: single-term search, multi-term AND search, missing
  terms, empty queries, posting-list explanation, and unloaded index errors.
- `tests/test_main.py`: command-level integration for `build`, `load`, `print`,
  `find`, `help`, `exit`, and invalid states.
- `tests/test_performance.py`: lightweight indexing and search performance over
  300 simulated pages.

## Git History

The repository history is organised as staged commits to show logical
development progression:

```text
chore: initialise coursework search tool structure
feat: add polite quotes crawler
feat: build persistent inverted index
feat: implement ranked search commands
test: expand coverage and performance checks
docs: document architecture and demonstration plan
```

The intended submission branch is `main`. For a new empty GitHub repository,
the local project can be connected and pushed with:

```powershell
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

If a remote named `origin` already exists:

```powershell
git remote set-url origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

## GenAI Use Declaration

Generative AI assistance was used during development. The main uses were:

- Interpreting the coursework brief and converting the requirements into a
  modular implementation plan.
- Drafting initial versions of the crawler, indexer, search, storage, CLI, and
  test files.
- Suggesting edge cases for the automated test suite.
- Improving documentation structure and preparing video explanation material.

The generated suggestions were checked against the coursework requirements and
validated through local testing. Several design decisions were made or verified
during review, including using a JSON index for inspectability, enforcing the
6 second politeness window in the crawler, storing word positions rather than
only page URLs, and using mocked crawler tests so that automated tests do not
depend on live network access.

The main benefit of GenAI was faster movement from the brief to a working
project structure. The main limitation was that generated code still required
manual validation: behaviour such as empty query handling, missing index files,
network failures, and schema validation had to be tested explicitly. The final
implementation was reviewed through the test suite, manual command-line runs,
and inspection of the generated `data/index.json` file.

## Submission Artifacts

The coursework submission consists of:

- Public GitHub repository URL containing the source code, tests, documentation,
  and generated index file.
- Video demonstration link, no longer than 5 minutes.
- Compiled index file: `data/index.json`.

The recommended video evidence is:

- Run `python -m pytest` and show the passing tests and coverage.
- Start the tool with `python -m src.main`.
- Demonstrate `load`, `print nonsense`, `find indifference`, and
  `find good friends`.
- Demonstrate at least one edge case such as `find` or
  `find wordthatdoesnotexist`.
- Show the staged Git history with `git log --oneline --decorate --graph`.
- Explain the role of GenAI critically, including both benefits and limitations.

