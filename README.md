
# 💀 Scuwl 💀

## Simple custom wordlist generator

Scuwl (skull) is a Python CLI program that quickly and easily generates a wordlist from a webpage. The idea for Scuwl was inspired by the program Cewl. Scuwl defaults to a crawling depth of zero and most webpages return a wordlist in less than a second. Using a crawling depth of one generally takes a few minutes.

Scuwl is fast because it recursively scrapes websites asynchronously.
Scuwl minimizes its memory footprint by processing HTML as it goes and updating the wordlist in memory as a set. By default Scuwl keeps unique words, three characters long and over, and removes all punctuation.

> Note: Using a crawling depth of over one remains untested.

## Features

- Fast recursive asynchronous web requests using aiohttp
- CLI options gives you control over the generated wordlist
- Simple Python codebase (< 150 lines)
- Low memory usage (~80MB)


## Installation

```bash
  python -m pip install scuwl
```
    
## Usage
```bash
$ scuwl -h
usage: scuwl.py [-h] [-d DEPTH] [-H HEADERS] [-m MIN_LENGTH] [-o OUTFILE]
                [-P PROXY] [-p] [-u USER_AGENT] [-v]
                url

💀SCuWl💀, Simple custom wordlist generator.

positional arguments:
  url                   url to scrape

options:
  -h, --help            show this help message and exit
  -d DEPTH, --depth DEPTH
                        depth of search
  -H HEADERS, --headers HEADERS
                        json headers for client
  -m MIN_LENGTH, --min-length MIN_LENGTH
                        minimum length of words to keep
  -o OUTFILE, --outfile OUTFILE
                        outfile for wordlist
  -P PROXY, --proxy PROXY
                        proxy address for client
  -p, --punctuation     keep punctutation
  -u USER_AGENT, --user-agent USER_AGENT
                        user-agent string for client
  -v, --version         show program's version number and exit

```

## Examples

```bash
Generate wordlist and send to stdout

$ scuwl https://github.com/petebuffon/scuwl
topics
out
scuwl
2022
track
...
```

```bash
Generate wordlist and save as wordlist.txt

$ scuwl -o wordlist.txt https://github.com/petebuffon/scuwl
$ wc -l wordlist.txt
122 wordlist.txt
```

```bash
Keep punctuation

$ scuwl -p -o wordlist.txt https://github.com/petebuffon/scuwl
$ head wordlist.txt
customer
wait?
write
devops
user
```

```bash
Use a crawl depth of one (scrapes all links from input webpage)

$ scuwl -d 1 -o wordlist.txt https://github.com/petebuffon/scuwl
$ wc -l wordlist.txt
6326 wordlist.txt
```
