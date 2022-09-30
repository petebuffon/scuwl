"""💀SCuWl💀, Simple custom wordlist generator."""
import argparse
import asyncio
import json
from signal import SIGINT, SIGTERM
from string import punctuation
from urllib.parse import urlparse, urlunparse
import aiohttp
from bs4 import BeautifulSoup, Comment

__version__ = "1.0"


def parse_arguments():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="💀SCuWl💀, Simple custom wordlist generator.")
    parser.add_argument("url", type=str, help="url to scrape")
    parser.add_argument("-d", "--depth", type=int, default=0, help="depth of search")
    parser.add_argument("-H", "--headers", type=str, default = "{}", help="json headers for client")
    parser.add_argument("-m", "--min-length", type=str, default=3,
                        help="minimum length of words to keep")
    parser.add_argument("-o", "--outfile", type=str, help="outfile for wordlist")
    parser.add_argument("-P", "--proxy", type=str, help="proxy address for client")
    parser.add_argument("-p", "--punctuation", action="store_false", help="keep punctutation")
    parser.add_argument("-u", "--user-agent", type=str, help="user-agent string for client")
    parser.add_argument("-v", "--version", action="version",
                        version=f"%(prog)s {__version__}")
    return parser.parse_args()


class Scraper:
    """Asynchronus web scraper."""
    def __init__(self, args, client):
        self.args = args
        self.client = client
        self.url = urlparse(args.url)
        self.sem = asyncio.Semaphore(60)
        self.wordlist = set()
        self.exclude_tags = {'style', 'script', 'head', 'title', 'meta', '[document]'}
        self.tasks = []

    async def fetch(self, url):
        """Fetches text from website."""
        async with self.sem:
            try:
                async with self.client.get(url, proxy=self.args.proxy) as resp:
                    return await resp.text() if (resp.status == 200) else ""
            except aiohttp.client_exceptions.InvalidURL:
                return ""

    async def recursive_scrape(self, url, depth):
        """Scrapes url for words and links at depth."""
        text = await self.fetch(url)
        soup = BeautifulSoup(text, "lxml")
        self.extract_words(soup)
        if depth == self.args.depth:
            return
        for link in self.extract_links(soup):
            task = asyncio.create_task(self.recursive_scrape(link, depth + 1))
            self.tasks.append(task)

    def extract_words(self, soup):
        """Extracts words from soup object."""
        trans_table = str.maketrans('', '', punctuation)
        visible_tags = soup.find_all(string=self.is_visible_tag)
        if self.args.punctuation:
            tags = (tag.lower().translate(trans_table) for tag in visible_tags)
            self.wordlist.update(self.filter_words(tags))
        else:
            tags = (tag.lower() for tag in visible_tags)
            self.wordlist.update(set(self.filter_words(tags)))

    def extract_links(self, soup):
        """Extracts links from soup object."""
        links = soup.find_all("a", href=True)
        for link in links:
            if link.text:
                if self.url.netloc in link["href"]:
                    yield link["href"]
                elif link["href"].startswith("/"):
                    yield self.build_url(link["href"])

    def write_to_file(self):
        """Writes wordlist set to outfile."""
        with open(self.args.outfile, "w", encoding="utf8") as file:
            file.writelines(f"{word}\n" for word in self.wordlist)

    def build_url(self, path):
        """Builds url from path and globals."""
        return urlunparse((self.url.scheme, self.url.netloc, path, None, "", ""))

    def filter_words(self, tags):
        """Filters out words based on CLI flags."""
        for tag in tags:
            for word in tag.split():
                if len(word) >= self.args.min_length and word.isascii():
                    yield word

    def is_visible_tag(self, element):
        """Returns True if tag is visible."""
        return (
                element.parent.name not in self.exclude_tags and
                not isinstance(element, Comment)
        )


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
    if args.user_agent:
        headers["user-agent"] = args.user_agent
    async with aiohttp.ClientSession(headers=headers) as client:
        scraper = Scraper(args, client)
        try:
            await scraper.recursive_scrape(args.url, 0)
            await asyncio.gather(*scraper.tasks)
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
