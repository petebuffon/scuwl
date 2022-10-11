"""💀SCuWl💀, Simple custom wordlist generator."""
import argparse
import asyncio
from hashlib import blake2b
import json
from signal import SIGINT, SIGTERM
from string import punctuation
from urllib.parse import urljoin, urlparse
import urllib.robotparser
from pkg_resources import get_distribution
import aiohttp
from bs4 import BeautifulSoup, Comment

__version__ = get_distribution("scuwl").version
TRANS_TABLE = str.maketrans("", "", punctuation)


def parse_arguments():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="💀SCuWl💀, Simple custom wordlist generator.")
    parser.add_argument("-a", "--alpha", action="store_true",
                        help="extract words with alphabet characters only, default=False")
    parser.add_argument("url", type=str, help="url to scrape")
    parser.add_argument("-d", "--depth", type=int, default=0, help="depth of search, default=0")
    parser.add_argument("-H", "--headers", type=str, default = "{}", help="json headers for client")
    parser.add_argument("-m", "--min-length", type=int, default=3,
                        help="minimum length of words to keep, default=3")
    parser.add_argument("-M", "--max-length", type=int, default=20,
                        help="maximum length of words to keep, default=20")
    parser.add_argument("-o", "--outfile", type=str, help="outfile for wordlist, default=stdout")
    parser.add_argument("-P", "--proxy", type=str, help="proxy address for client")
    parser.add_argument("-p", "--punctuation", action="store_false",
                        help="retains punctutation in words")
    parser.add_argument("-t", "--tables", action="store_true",
                        help="extract words from tables only, default=False")
    parser.add_argument("-T", "--timeout", type=int, default=20,
                        help="session timeout for each request")
    parser.add_argument("-u", "--user-agent", type=str, default="scuwl/" + __version__,
                        help="user-agent string for client")
    parser.add_argument("-v", "--version", action="version",
                        version=f"%(prog)s {__version__}")
    return parser.parse_args()


class Scraper:
    """Asynchronus web scraper."""
    def __init__(self, args, session):
        self.args = args
        self.sem = asyncio.Semaphore(60)
        self.session = session
        self.url = urlparse(args.url)
        self.robotparser = build_robotparser(self.url.netloc)
        self.urls = set()
        self.tasks = []
        self.wordlist = set()

    async def fetch(self, url):
        """Fetches text from website."""
        async with self.sem:
            try:
                async with self.session.get(url, proxy=self.args.proxy) as resp:
                    if resp.status == 200:
                        content_type = resp.headers.get("Content-Type", "")
                        if "text/html" in content_type or not content_type:
                            return await resp.text()
                    else:
                        return ""
            except (aiohttp.ClientError, UnicodeDecodeError,
                    AssertionError, asyncio.exceptions.TimeoutError):
                return ""

    async def recursive_scrape(self, url, depth):
        """Scrapes url for words and links at depth."""
        text = await self.fetch(url)
        if not text:
            return
        soup = BeautifulSoup(text, "lxml")
        if self.args.tables:
            self.extract_tables(soup)
        else:
            self.extract_words(soup)
        if depth == self.args.depth:
            return
        for link in self.extract_links(soup):
            task = asyncio.create_task(self.recursive_scrape(link, depth + 1))
            self.tasks.append(task)

    def extract_words(self, soup):
        """Extracts words from soup object."""
        visible_tags = soup.find_all(string=self.is_visible_tag)
        if self.args.punctuation:
            tags = (tag.lower().translate(TRANS_TABLE) for tag in visible_tags)
        else:
            tags = (tag.lower() for tag in visible_tags)
        self.wordlist.update(self.filter_words(tags))

    def extract_links(self, soup):
        """Extracts links from soup object."""
        links = soup.find_all("a", href=True)
        for link in links:
            if link.text:
                if link["href"].endswith(".svg") or link["href"].endswith(".jpg"):
                    continue
                if self.url.netloc in link["href"]:
                    if link["href"].startswith("//"):
                        url = urljoin((self.url.scheme + "://" + self.url.netloc), link["href"])
                    else:
                        url = link["href"]
                elif not link["href"].startswith("#"):
                    url = urljoin((self.url.scheme + "://" + self.url.netloc), link["href"])
                if not self.robotparser.can_fetch(self.session.headers["user-agent"], url):
                    continue
                _hash = blake2b(url.encode("utf8"), digest_size=32).digest()
                if _hash not in self.urls:
                    self.urls.add(_hash)
                    yield url

    def extract_tables(self, soup):
        """Extracts tables from soup object."""
        tables = soup.find_all("table")
        if self.args.punctuation:
            text = (table.text.lower().translate(TRANS_TABLE) for table in tables)
        else:
            text = (table.text.lower() for table in tables)
        self.wordlist.update(self.filter_words(text))

    def write_to_file(self):
        """Writes wordlist set to outfile."""
        with open(self.args.outfile, "w", encoding="utf8") as file:
            file.writelines(f"{word}\n" for word in self.wordlist)

    def filter_words(self, tags):
        """Filters out words based on CLI flags."""
        for tag in tags:
            for word in tag.split():
                if len(word) >= self.args.min_length and len(word) <= self.args.max_length:
                    if self.args.alpha and word.isalpha():
                        yield word
                    elif word.isascii():
                        yield word

    def is_visible_tag(self, element):
        """Returns True if tag is visible."""
        exclude_tags = {"style", "script", "head", "title", "meta", "[document]"}
        return (
                element.parent.name not in exclude_tags and
                not isinstance(element, Comment)
        )


def build_robotparser(netloc):
    """Builds robotparser from netloc"""
    robotparser = urllib.robotparser.RobotFileParser()
    robotparser.set_url("https://" + netloc + "/robots.txt")
    robotparser.read()
    return robotparser


def shutdown():
    """Shuts down running loop."""
    loop = asyncio.get_running_loop()
    for task in asyncio.all_tasks(loop=loop):
        task.cancel()
    loop.remove_signal_handler(SIGTERM)
    loop.add_signal_handler(SIGINT, lambda: None)


def add_signal_handlers():
    """Adds SIGINT AND SIGTERM signal handlers to running loop."""
    loop = asyncio.get_running_loop()
    for sig in (SIGINT, SIGTERM):
        loop.add_signal_handler(sig, shutdown)


async def generate_wordlist():
    """Generates wordlist."""
    args = parse_arguments()
    add_signal_handlers()
    headers = json.loads(args.headers)
    headers["user-agent"] = args.user_agent
    timeout = aiohttp.ClientTimeout(total=args.timeout)

    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        scraper = Scraper(args, session)
        try:
            await scraper.recursive_scrape(args.url, 0)
            await asyncio.gather(*scraper.tasks)
            scraper.wordlist = sorted(scraper.wordlist)
            if scraper.args.outfile:
                scraper.write_to_file()
            else:
                for word in scraper.wordlist:
                    print(word)
        except asyncio.CancelledError:
            print()


def main():
    """Main function to start async loop."""
    asyncio.run(generate_wordlist())


if __name__ == "__main__":
    main()
