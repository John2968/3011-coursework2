# COMP3011 Coursework 2: Search Engine Tool

This project implements a Python command-line search tool for
[`https://quotes.toscrape.com/`](https://quotes.toscrape.com/). It crawls the
quote listing pages, builds an inverted index with word statistics, saves the
compiled index to disk, and lets the user search the index from an interactive
shell.

## Features

- Polite crawler with a default 6 second delay between successive requests.
- Robust HTML parsing using Beautiful Soup, with fallbacks for missing quote
  blocks or title elements.
- Inverted index storing document frequency, term frequency, and word
  positions for each page.
- Persistent JSON index file with schema version validation.
- Case-insensitive `print` and `find` commands.
- Multi-word search using AND semantics, ranked with a BM25-style score.
- Unit, integration, CLI, and performance tests with coverage above 85%.

## Project Structure

```text
repository-name/
  src/
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
  README.md
  VIDEO_SCRIPT.md
```

## Setup

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If you do not want to create a virtual environment, install the requirements
directly with:

```powershell
python -m pip install -r requirements.txt
```

## Usage

Start the interactive shell:

```powershell
python -m src.main
```

The shell supports the required coursework commands:

```text
> build
> load
> print nonsense
> find indifference
> find good friends
```

`build` crawls the target website, creates the index, and saves it to
`data/index.json`. Because the coursework requires a politeness window, a full
live build intentionally takes time. `load` reads the saved index back from the
file system. `print <word>` shows the posting list for one word. `find
<query...>` returns pages containing all query terms, ranked by relevance.

You can use a custom index path if needed:

```powershell
python -m src.main --index-path data/index.json
```

## Inverted Index Design

The index is stored as JSON so it can be inspected easily during marking and in
the video demonstration. Its main structure is:

- `metadata`: schema version, source site, creation timestamp, document count,
  and average document length.
- `documents`: a mapping from stable document IDs to URL, title, preview, and
  token count.
- `terms`: a mapping from normalised words to document frequency and postings.
- `postings`: for each word and document, frequency and token positions.

This structure gives efficient lookup for `print <word>` because each term maps
directly to its posting list. It also supports multi-word `find` by intersecting
document ID sets and then ranking the remaining documents. Word positions make
the index richer than a simple word-to-URL mapping and provide evidence for the
coursework requirement to store word statistics.

## Search Strategy

Tokenisation lowercases input and keeps alphanumeric words, so `Good`, `good`,
and `GOOD` match the same term. Multi-word queries use AND semantics because the
brief asks for pages containing all query words. Results are ranked with a
BM25-style score using term frequency, document frequency, document length, and
average document length. This is a useful extension beyond the minimum
requirements while keeping the implementation explainable in a 5-minute video.

## Testing

Run the full test suite with coverage:

```powershell
python -m pytest
```

The suite includes:

- Crawler tests with mocked HTTP responses, pagination, fallback parsing, and
  request failure handling.
- Indexer tests for tokenisation, case insensitivity, frequency, positions, and
  empty text.
- Storage tests for save/load round trips, missing files, invalid JSON, and
  schema validation.
- Search tests for single-term and multi-term queries, missing words, and
  unloaded index errors.
- CLI tests for all required commands.
- A lightweight performance test using simulated pages.

Current local result:

```text
19 passed
TOTAL coverage: 90%
```

## Git Workflow

Recommended workflow for the coursework:

```powershell
git init
git checkout -b feature/search-engine-tool
git add .
git commit -m "chore: initialise coursework search tool structure"
```

Then commit logical stages as the project develops, for example crawler,
indexing, search, tests, and documentation. This gives a clear history to show
in the video demonstration.

To connect this local project to GitHub in VSCode/Cursor:

1. Create a new public repository on GitHub, without adding a README because
   this project already has one.
2. In VSCode/Cursor, open Source Control and sign in to GitHub if prompted.
3. Add the remote URL in the terminal:

```powershell
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin feature/search-engine-tool
```

You can then create a pull request on GitHub or merge the branch into `main`.
For Minerva, submit the public GitHub repository URL, the video link, and the
compiled `data/index.json` file.

## GenAI Declaration and Reflection Notes

Generative AI was used as an assisted development tool for planning, code
structure, tests, and documentation. The code was reviewed and tested locally,
and AI-generated suggestions were adjusted to match the coursework brief, for
example by enforcing the 6 second politeness window and choosing an inspectable
JSON index format.

Useful critical reflection points for the video:

- AI helped quickly translate the brief into a modular architecture.
- AI suggestions still needed human checking against the marking criteria.
- Tests were important because generated code can miss edge cases such as empty
  queries, missing index files, and network failures.
- Building and explaining the index data structure improved understanding of
  search engine mechanisms rather than simply accepting generated code.

## Submission Checklist

- Run `python -m pytest` and confirm coverage remains above 85%.
- Run `python -m src.main`, then demonstrate `build`, `load`, `print`, and
  `find`.
- Ensure `data/index.json` exists and is included in the submission.
- Push the repository to GitHub and copy the public repository URL.
- Record a video no longer than 5 minutes and verify the link in a private
  browser window.
- Submit one TXT or PDF document on Minerva containing the video link, GitHub
  URL, and index file attachment or link.

