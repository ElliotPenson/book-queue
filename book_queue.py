"""
book-queue.py

@author Elliot Penson
"""

import argh
from jinja2 import Environment, PackageLoader, select_autoescape

from good_reads_user import GoodReadsUser


def main(user_id, api_key):
    user = GoodReadsUser(user_id, api_key)
    shelves = [
        {
            'title': 'Read',
            'books': reversed(list(user.get_shelf('read', 'date_read')))
        },
        {
            'title': 'Currently Reading',
            'books': user.get_shelf('currently-reading', 'date_added')
        },
        {
            'title': 'To-Read',
            'books': user.get_shelf('to-read', 'position')
        }
    ]
    render_template('generated/index.html', shelves=shelves)


def render_template(output_file, **data):
    env = Environment(
        loader=PackageLoader('book_queue', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('index.html')
    output = template.render(**data)
    with open(output_file, 'w') as f:
        f.write(output)


if __name__ == '__main__':
    argh.dispatch_command(main)
