"""
book-queue.py

@author Elliot Penson
"""

import sys
import os
import xml.etree.ElementTree as ET

import requests
from jinja2 import Environment, PackageLoader, select_autoescape


_, GOOD_READS_API_KEY, USER_ID = sys.argv


def get_shelf(name, sort_by=None, user_id=USER_ID):
    """
    Request all books from a specific member's bookshelf.
    :return: A list of dicts (keys: id, title, image, authors, read_at, rating)
    """
    payload = {
        'id': user_id,
        'shelf': name,
        'sort': sort_by or 'date_added',
        'key': GOOD_READS_API_KEY
    }
    response = requests.get('https://www.goodreads.com/review/list?v=2', params=payload)
    return parse_shelf_response(response.text)


def parse_shelf_response(xml):
    """Converts an GoodReads XML response into a python dict."""
    tree = ET.fromstring(xml)
    for review in tree.iter('review'):
        book = review.find('book')
        book_id = book.find('id').text
        yield {
            'id': book_id,
            'title': remove_subtitle(book.find('title_without_series').text),
            'image': scrub_image(book.find('image_url').text, book_id),
            'authors': [author.find('name').text for author in book.iter('author')],
            'read_at': review.find('read_at').text,
            'rating': int(review.find('rating').text)
        }


def remove_subtitle(title):
    """Strip a book's subtitle (if it exists). For example, 'A Book: Why Not?' becomes 'A Book'."""
    if ':' in title:
        return title[:title.index(':')].strip()
    else:
        return title


def scrub_image(url, book_id):
    """
    Test if the given url contains a particular book's cover. If not, try and find an appropriate
    image in the assets folder.
    """
    if 'nophoto' in url:
        cover_image = 'no-cover.png'
        for potential_image in os.listdir('assets/images/covers/'):
            if book_id in potential_image:
                cover_image = potential_image
        return os.path.join('images/covers/', cover_image)
    else:
        return url


def render_template(path='generated/index.html'):
    env = Environment(
        loader=PackageLoader('book-queue', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('index.html')
    output = template.render(sections=[
        {
            'title': 'Read',
            'books': reversed(list(get_shelf('read', 'date_read')))
        },
        {
            'title': 'Currently Reading',
            'books': get_shelf('currently-reading', 'date_added')
        },
        {
            'title': 'To-Read',
            'books': get_shelf('to-read', 'position')
        }
    ])
    with open(path, 'w') as f:
        f.write(output)


if __name__ == '__main__':
    render_template()
