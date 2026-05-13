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

"I used Cursor/GPT as an assistant for planning the architecture, generating
initial code, and suggesting tests. It helped me move quickly from the brief to
a modular structure, but I still had to verify the suggestions against the
requirements. For example, I checked that the crawler really respects the 6
second politeness window and that the index stores frequency and positions, not
just words. The most useful part was using AI to identify edge cases for tests.
The limitation was that AI-generated code can look correct before it is tested,
so running coverage and reading the generated index were important for my own
understanding."

