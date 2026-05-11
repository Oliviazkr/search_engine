# Search Engine Tool - XJCO3011 Coursework 2

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

## Testing
```bash
python -m pytest tests/ -v

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
