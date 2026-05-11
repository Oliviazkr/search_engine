# Search Engine Tool - XJCO3011 Coursework 2

## Project Overview

This project implements a command-line search engine tool that crawls a website, builds an inverted index, and supports search queries. It was developed as part of the XJCO3011 Web Services and Web Data module at the University of Leeds.

**Purpose:** To demonstrate understanding of web crawling, inverted indexing, and search algorithms.

**Target Website:** https://quotes.toscrape.com/

**Key Features:**
- Crawls all pages with a 6-second politeness window
- Builds inverted index with word frequency and position statistics
- Supports single-word and multi-word queries
- Persistent index storage (save/load to disk)
- Case-insensitive search

## Installation
```bash
pip install -r requirements.txt
```
## Usage
```bash
python src/main.py
```
## Commands
```bash
build                     - Crawl website and build index
load                      - Load saved index from disk
print <word>              - Show inverted index for a word
find <phrase>             - Search for pages
stats                     - Show index statistics
exit                      - Quit program
```
## Example
```bash
> build
Crawl complete. 10 pages indexed.

> find love
Found 8 page(s) containing 'love':
  https://quotes.toscrape.com/ (relevance: 4)

> print life
Inverted index for 'life':
  https://quotes.toscrape.com/
    Frequency: 4
    Positions: [15, 23, 31, 42]

> load
Index loaded from data/index.json
```
## Testing
```bash
python -m pytest tests/ -v
```
## Project Structure
```bash
search_engine/
├── src/
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   ├── storage.py
│   └── main.py
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── data/
├── requirements.txt
└── README.md

## Notes

- Politeness window: 6 seconds between requests
- Case-insensitive: 'Good' = 'good'
- First run: Use 'build' to create index (takes 3-4 minutes)
- Subsequent runs: Use 'load' to load saved index
