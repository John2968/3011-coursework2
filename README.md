# COMP3011 Search Engine Tool

A Python command-line search tool for
[`quotes.toscrape.com`](https://quotes.toscrape.com/). The application crawls
the quote listing pages, builds an inverted index with word statistics, stores
the compiled index as JSON, and supports interactive search over the saved
index.

The project demonstrates the main components of a small search engine:

- polite web crawling
- HTML parsing
- tokenisation and normalisation
- inverted index construction
- persistent index storage
- command-line query processing
- ranked multi-term search
- automated testing

## Features

- Crawls the paginated quote pages from `https://quotes.toscrape.com/`.
- Uses a default 6 second politeness window between HTTP requests.
- Extracts quote text, authors, and tags with Beautiful Soup.
- Falls back to page-level text extraction if the expected quote layout is not available.
- Builds a case-insensitive inverted index.
- Stores document frequency, term frequency, token positions, document length, URL, title, and preview text.
- Saves and loads the compiled index from `data/index.json`.
- Supports `build`, `load`, `print`, `find`, `help`, and `exit` in an interactive shell.
- Handles missing index files, empty queries, unknown commands, missing command arguments, missing words, and request failures with readable messages.
- Uses a BM25-style ranking score for matched search results.
- Includes unit, integration, command-level, and performance tests.

## Project Structure

```text
3011-coursework2/
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

Python 3.12 was used for development and testing.

Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The runtime dependencies are:

- `requests`
- `beautifulsoup4`

The test dependencies are:

- `pytest`
- `pytest-cov`

## Running the Application

Start the interactive shell from the repository root:

```powershell
python -m src.main
```

The default index file path is `data/index.json`. A custom index path can be provided with:

```powershell
python -m src.main --index-path path/to/index.json
```

## Command Reference

The shell accepts command syntax rather than a fixed set of example queries.

`build`

Crawls the target website, builds a new inverted index, saves it to disk, and loads it into memory. Because the crawler follows a 6 second politeness window, a full live build intentionally takes time.

`load`

Loads a previously saved index file from disk. This allows searching without crawling the website again.

`print <word>`

Prints the posting list for one word. The output includes document frequency, page URLs, term frequency within each page, and token positions.

`find <query terms>`

Searches for pages containing all query terms. Matching is case-insensitive. Results are ordered by a BM25-style relevance score and include page URL, score, per-term frequencies, and preview text.

`help`

Displays the available shell commands.

`exit`

Closes the interactive shell.

## Example Session

The following session shows typical usage. The exact number of unique terms may change if the website content or tokenisation rules change.

```text
> build
Built index from 10 page(s).
Indexed 849 unique term(s).
Saved index to data\index.json.

> load
Loaded index from data\index.json.
10 page(s), 849 unique term(s).

> print nonsense
Term: nonsense
Document frequency: 1
- https://quotes.toscrape.com/page/6/ | freq=1 | positions=[...]

> find good friends
Results for: good friends
1. https://quotes.toscrape.com/...
   score=...
   good=..., friends=...
   ...
```

Examples of valid search commands include:

```text
> find indifference
> find good friends
> find GOOD Friends
> print love
> print truth
```

## Architecture

The implementation is separated into small modules with clear responsibilities.

`src/crawler.py`

Implements `QuotesCrawler`, which performs polite HTTP requests, follows pagination, parses HTML with Beautiful Soup, extracts quote content, and handles request failures.

`src/indexer.py`

Implements tokenisation, normalisation, document ID generation, preview generation, and inverted index construction.

`src/search.py`

Implements query normalisation, posting-list lookup, multi-term AND matching, BM25-style scoring, and formatted search output.

`src/storage.py`

Handles JSON persistence for the compiled index and validates the stored schema version when loading.

`src/main.py`

Provides the interactive command-line interface and connects the crawler, indexer, storage layer, and search engine.

`src/models.py`

Defines dataclasses for crawled pages, documents, postings, term entries, complete indexes, and ranked search results.

## Inverted Index Design

The index is stored as readable JSON in `data/index.json`. Its main sections are:

- `metadata`: schema version, source site, creation timestamp, document count, and average document length.
- `documents`: document IDs mapped to URL, title, preview text, and token count.
- `terms`: normalised words mapped to document frequency and postings.
- `postings`: per-document term frequency and token positions for each word.

Simplified structure:

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

This structure supports direct lookup for `print <word>` and efficient multi-term search by intersecting posting-list document IDs. Storing token positions provides more detail than a simple word-to-URL mapping and makes the index easier to inspect and explain.

## Search Strategy

Input text is lowercased and tokenised with a regular expression that keeps alphanumeric words and simple apostrophe forms. Searches are therefore case-insensitive.

Multi-term queries use AND semantics: a page must contain every query term to appear in the results. Matching pages are ranked using a BM25-style score based on:

- term frequency in the document
- document frequency across the collection
- document length
- average document length

The ranking layer is intentionally compact: it improves result ordering while remaining understandable for a small coursework search engine.

## Error Handling

The application uses defensive checks around common failure cases:

- request timeouts and HTTP errors during crawling
- missing or invalid index files during loading
- unsupported index schema versions
- empty commands
- unknown commands
- missing arguments for `print` and `find`
- searches before an index has been built or loaded
- terms that do not exist in the index

Example messages:

```text
> find
Usage: find <word or phrase>

> print
Usage: print <word>

> find wordthatdoesnotexist
No pages found containing all terms: wordthatdoesnotexist
```

## Testing

Run the test suite with coverage:

```powershell
python -m pytest
```

Current local result:

```text
20 passed
TOTAL coverage: 90%
```

The testing strategy combines unit tests, integration-style command tests, and a
lightweight performance test.

Unit tests cover:

- crawler pagination and HTML extraction
- crawler fallback parsing and request failure handling
- tokenisation and case-insensitive indexing
- term frequency, document frequency, and token positions
- JSON save/load behaviour
- missing files, invalid JSON, and schema validation
- single-term and multi-term search
- empty and missing query handling

Integration-style tests cover the command-level behaviour for `build`, `load`,
`print`, `find`, `help`, and `exit` through the `SearchTool` command handler.

The performance test builds and searches an index over 300 simulated pages to
check that indexing and query processing remain fast for a larger in-memory
dataset than the live target site.

The crawler tests use mocked HTTP responses so the automated suite does not depend on live network availability or the 6 second politeness delay.

## Development History

The Git history is organised into staged semantic commits:

```text
chore: initialise coursework search tool structure
feat: add polite quotes crawler
feat: build persistent inverted index
feat: implement ranked search commands
test: expand coverage and performance checks
docs: document architecture and demonstration plan
```

This progression reflects the main implementation stages: project setup, crawling, indexing and storage, search and CLI behaviour, tests, and documentation.

## GenAI Use

Generative AI assistance was used during development. The main tool used was
Cursor with GPT-based chat and coding assistance. It was used for requirements
analysis, project planning, initial code drafting, test case suggestions,
debugging support, and documentation drafting.

AI support was useful at the planning stage because it helped convert the
coursework brief into a modular structure with separate crawler, indexer,
storage, search, command-line, and test components. It also helped identify
important behaviours to test, such as empty queries, missing index files,
network request failures, and schema validation.

The AI-generated suggestions were not accepted without review. The code was
checked against the coursework requirements through manual inspection,
command-line runs, automated tests, and inspection of the generated
`data/index.json` file. Particular attention was given to verifying that the
crawler respects the 6 second politeness window, that the index stores term
frequency and token positions rather than only page URLs, and that the `find`
command handles multi-word queries correctly.

There were also limitations. Some AI suggestions were too generic and needed to
be adapted to the exact coursework website and command requirements. The test
suite also needed manual review because generated tests can miss edge cases or
test only the expected path. Mocked crawler tests were added so the automated
tests would not depend on live network access or wait for the politeness delay.

Using GenAI improved development speed and helped with time management, but it
also created an extra responsibility to understand and validate the generated
code. The learning benefit came from checking why each part was needed: how
Beautiful Soup extracts HTML elements, why an inverted index supports efficient
lookup, how posting-list intersections support multi-word search, and how BM25-
style ranking uses term frequency, document frequency, and document length.

The final implementation keeps the core search engine concepts visible in the
code: crawling, tokenisation, posting lists, word positions, persistent storage,
and ranked retrieval.
