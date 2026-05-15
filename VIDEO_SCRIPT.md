# 5-Minute Video Demonstration Script

Use this as a guide rather than reading it word for word. Keep the screen zoomed
in enough for the terminal and code to be readable.

## 0:00-0:20 Introduction

"This is my COMP3011 Coursework 2 search engine tool. It crawls
quotes.toscrape.com, builds an inverted index, stores the index as JSON, and
provides a command-line shell for loading, printing, and searching the index."

Show the repository structure: `src/`, `tests/`, `data/`, `README.md`.

## 0:20-2:20 Live Demonstration

Open a terminal and run:

```powershell
python -m src.main
```

Demonstrate:

```text
> build
> load
> print nonsense
> find indifference
> find good friends
> find
> find wordthatdoesnotexist
```

Explain that `build` observes the 6 second politeness window, so for the video it
is acceptable to show a previously generated `data/index.json` after explaining
that the live build takes time by design.

## 2:20-3:50 Code Walkthrough and Design Decisions

Show these files briefly:

- `src/crawler.py`: `QuotesCrawler` follows pagination, uses Requests and
  Beautiful Soup, handles request exceptions, and has fallback parsing.
- `src/indexer.py`: tokenisation is lowercase and case-insensitive; the builder
  records term frequency and positions.
- `src/models.py`: dataclasses keep the index structure clear.
- `src/search.py`: `find` intersects posting lists and ranks matching documents
  with a BM25-style score.
- `src/storage.py`: JSON persistence with schema validation.

Design points to mention:

- The inverted index maps a word directly to its posting list, which makes
  `print <word>` efficient.
- Positions support richer word statistics than a simple set of URLs.
- JSON was chosen because it is inspectable and easy to submit as the compiled
  index file.
- BM25-style ranking is an extension beyond the minimum requirements but remains
  simple enough to explain.

## 3:50-4:20 Testing Demonstration

Run:

```powershell
python -m pytest
```

Mention:

- Unit tests cover crawler, indexer, search, and storage.
- Integration-style CLI tests cover `build`, `load`, `print`, and `find`.
- The performance test checks indexing and searching over simulated pages.
- Coverage is above the 85% target.

## 4:20-4:40 Version Control

Show:

```powershell
git log --oneline --decorate --graph
```

Explain that the commits are grouped by project stage: structure, crawler,
indexing/search, tests, documentation, and generated index.

## 4:40-5:00 GenAI Critical Evaluation

Suggested concise reflection:

"I used Cursor with GPT-based assistance for planning the architecture, drafting
initial code, suggesting tests, debugging, and improving documentation. It
helped me move faster from the brief to a modular structure with separate
crawler, indexer, storage, search, and test components. However, I did not treat
the AI output as automatically correct. I checked that the crawler respects the
6 second politeness window, that the inverted index stores frequency and token
positions, and that multi-word queries work through posting-list intersection.
One limitation was that some AI suggestions were too generic, so I had to adapt
them to the exact website and command requirements. AI also suggested useful
tests, but I still had to add and verify edge cases such as empty queries,
missing files, and network failures. Overall, GenAI improved my time management,
but it also forced me to review, test, and understand the implementation rather
than simply accepting generated code."

