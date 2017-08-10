import os
import xml.etree.ElementTree as ET

import requests

GOOD_READS_SHELF_URL = 'https://www.goodreads.com/review/list?v=2'


class GoodReadsUser:

    def __init__(self, user_id, api_key):
        self.user_id = user_id
        self.api_key = api_key

    def get_shelf(self, name, sort_by=None):
        """
        Request all books from a specific member's bookshelf.
        :return: A list of dicts (keys: id, title, image, authors, read_at, rating)
        """
        payload = {
            'id': self.user_id,
            'shelf': name,
            'sort': sort_by or 'date_added',
            'key': self.api_key
        }
        response = requests.get(GOOD_READS_SHELF_URL, params=payload)
        return GoodReadsUser.parse_shelf_response(response.text)

    @classmethod
    def parse_shelf_response(cls, xml):
        """Convert a GoodReads XML response into a python dict."""
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