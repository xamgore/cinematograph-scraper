#!/usr/bin/env -S pipenv run python
from collections import defaultdict

import bs4
from glob import iglob
import json
from pathlib import Path
import requests

if __name__ == '__main__':
    authorToMaterials = defaultdict(set)

    for path in iglob('./journal/**/short.json', recursive=True):
        content = Path(path).read_text()
        article = json.loads(content, parse_constant=True)

        for a in article['authors']:
            authorToMaterials[a['href']].add(article['url'])

    authors = {}

    for url, setOfArticles in authorToMaterials.items():
        print(url)
        host = 'https://cinematograph.media'
        content = requests.get(host + url).text
        root = bs4.BeautifulSoup(content, 'html.parser')

        authors[url] = {
            'url':       str(url),
            'name':      root.select_one('.author-bio__name').get_text().strip(),
            'status':    root.select_one('.author-bio__status').get_text().strip(),
            'bio':       root.select_one('.author-bio__description').get_text().strip(),
            'links':     [l.attrs['href'] for l in root.select('.author-bio__link')],
            'materials': list(setOfArticles),
        }

    content = json.dumps(authors, ensure_ascii=False, indent=2)
    Path('journal/authors.json').write_text(content)
