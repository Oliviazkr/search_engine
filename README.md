# XJCO3011 Coursework 2: Search Engine Tool

## Project Overview

A command-line search engine tool that crawls [quotes.toscrape.com](https://quotes.toscrape.com/), builds an inverted index, and provides search functionality. Built for the Web Services and Web Data module at the University of Leeds.

### Features

- **Web Crawler**: Respects politeness window (6 seconds between requests)
- **Inverted Index**: Stores word frequency and position information
- **Case-Insensitive Search**: 'Good' and 'good' are treated the same
- **Phrase Search**: Find pages containing all words in a query
- **Persistent Storage**: Save/load index to disk
- **Command Line Interface**: Four main commands (build, load, print, find)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <your-repository-url>
cd search_engine
