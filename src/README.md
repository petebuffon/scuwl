
# 💀 Scuwl 💀

## Simple custom wordlist generator

Scuwl (skull) is a Python CLI program that quickly and easily generates a wordlist from a webpage. The idea for Scuwl was inspired by the program Cewl. Scuwl defaults to a crawling depth of zero and most webpages return a wordlist in less than a second. Using a crawling depth of one generally takes a few minutes.

Scuwl is fast because it recursively scrapes websites asynchronously.
Scuwl minimizes its memory footprint by processing HTML as it goes and updating the wordlist in memory as a set. By default Scuwl keeps unique words, three characters long and over, and removes all punctuation.

> Note: Using a crawling depth of over one remains untested.

## Features

- Fast recursive asynchronous web requests using aiohttp
- CLI options gives you control over the generated wordlist
- Simple Python codebase (< 175 lines)
- Low memory usage (~100MB)


## Installation

```
  $ python -m pip install scuwl
```
    
## Usage
```
$ scuwl -h
usage: scuwl.py [-h] [-a] [-d DEPTH] [-H HEADERS] [-m MIN_LENGTH]
                [-M MAX_LENGTH] [-o OUTFILE] [-P PROXY] [-p] [-t]
                [-u USER_AGENT] [-v]
                url

💀SCuWl💀, Simple custom wordlist generator.

positional arguments:
  url                   url to scrape

options:
  -h, --help            show this help message and exit
  -a, --alpha           extract words with alphabet characters only,
                        default=False
  -d DEPTH, --depth DEPTH
                        depth of search, default=0
  -H HEADERS, --headers HEADERS
                        json headers for client
  -m MIN_LENGTH, --min-length MIN_LENGTH
                        minimum length of words to keep, default=3
  -M MAX_LENGTH, --max-length MAX_LENGTH
                        maximum length of words to keep, default=20
  -o OUTFILE, --outfile OUTFILE
                        outfile for wordlist, default=stdout
  -P PROXY, --proxy PROXY
                        proxy address for client
  -p, --punctuation     retains punctutation in words
  -t, --tables          extract words from tables only, default=False
  -u USER_AGENT, --user-agent USER_AGENT
                        user-agent string for client
  -v, --version         show program's version number and exit
```

## Examples

```
Generate wordlist and send to stdout

$ scuwl https://github.com/petebuffon/scuwl
1000
122
150
2022
20220930
...
```

```
Generate wordlist and save as wordlist.txt

$ scuwl -o wordlist.txt https://github.com/petebuffon/scuwl
$ wc -l wordlist.txt
309 wordlist.txt
```

```
Keep punctuation

$ scuwl -p -o wordlist.txt https://github.com/petebuffon/scuwl
$ head wordlist.txt
(2022-09-30)
(scrapes
(skull)
(~80mb)
--depth
```

```
Use a crawl depth of one (scrapes all links from input webpage)

$ scuwl -d 1 -o wordlist.txt https://github.com/petebuffon/scuwl
$ wc -l wordlist.txt
6675 wordlist.txt
```
