#!/usr/bin/env -S pipenv run python
from itertools import chain

from bs4 import BeautifulSoup, Tag
from json import dumps
from pathlib import Path
from requests import post
from typing import Union

INDEX_FOR = {
    'articles':   2,
    'reviews':    3,
    'interviews': 4
}

TYPES = INDEX_FOR.keys()


def take_while(predicate, iterable):
    while True:
        try:
            element = next(iterable)
            if not predicate(element):
                break
            yield element
        except StopIteration:
            break


def fetch(type, page_num=1):
    print(type, page_num)
    url = f'https://cinematograph.media/journal/index.php?PAGEN_{INDEX_FOR[type]}={page_num}'
    res = post(url, data={'AJAX': 'Y', 'type': type})
    return res.text


def fetch_all(type):
    htmls = (fetch(type, page_num) for page_num in range(1, 10_000))
    htmls = take_while(lambda s: len(s) > 0, htmls)
    return chain.from_iterable(map(parse, htmls))


def parse(html):
    root = BeautifulSoup(html, 'html.parser')
    for item in root.select('.card'):
        print(item.attrs['href'])
        item: Tag = item
        yield {
            'href':  item.attrs['href'],
            'img':   item.select_one('.card__image').attrs['src'],
            'title': item.select_one('.card__title').get_text().strip()
        }


def dump(type, folder: Union[str, Path] = ''):
    if isinstance(folder, str):
        folder = Path(folder)

    json = dumps(list(fetch_all(type)), ensure_ascii=False, indent=2)

    folder.mkdir(parents=True, exist_ok=True)
    (folder / (type + '.json')).write_text(json)


if __name__ == '__main__':
    for type in TYPES:
        dump(type, 'journal')
