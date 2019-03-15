import time

from bs4 import BeautifulSoup
import dateparser
import json
from json import dumps
from pathlib import Path
import re
from requests import get
from typing import Dict, Tuple


def parse(url: str) -> Tuple[Dict, str]:
    host = 'https://cinematograph.media'
    source = get(host + url).text
    root = BeautifulSoup(source, 'html.parser')

    date = root.select_one('.article-detailed-container__time').get_text().strip()

    data = {
        'url':       url,
        'id':        Path(url).stem,
        'type':      Path(url).parent.stem,
        'fetchTime': int(time.time()),
        'title':     root.select_one('.banner__title').get_text().strip(),
        'date':      int(dateparser.parse(date, languages=['ru']).timestamp()),
        'views':     int(root.select_one('.banner__views').get_text().strip()),
        'banner':    root.select_one('.banner__image').attrs['src'],
        'authors':   [{
            'href': a.attrs['href'],
            'name': a.get_text().strip(),
        } for a in root.select('.banner__author a')],
        'origins':   [{
            'href':  a.attrs['href'],
            'title': a.get_text().strip(),
        } for a in root.select('.origin__list .origin__link')],
        'tags':      [a.get_text().strip() for a in root.select('.tags__list .tags__link')],
    }

    # article = root.select_one('article').prettify(formatter="none")
    content = re.findall('<article[^>]*>(.*?)</article>', source, re.DOTALL)[0]
    return data, content


def fetch_and_dump(url: str):
    data, content = parse(url)
    data_with_article = dict(**data, content=content)

    path = Path('.' + url)
    path.mkdir(parents=True, exist_ok=True)
    (path / 'short.json').write_text(dumps(data, ensure_ascii=False, indent=2))
    (path / 'full.json').write_text(dumps(data_with_article, ensure_ascii=False, indent=2))
    (path / 'content.html').write_text(content)


if __name__ == '__main__':
    from journal import TYPES

    for type in TYPES:
        content = (Path('journal') / (type + '.json')).read_text()
        for page in json.loads(content):
            print(page['href'])
            fetch_and_dump(page['href'])
