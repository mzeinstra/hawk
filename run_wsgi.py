"""Script for start of aplication in wsgi"""

import os

from app import app_factory

app = app_factory(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config_wsgi.py'))

if __name__ == "__main__":
    app.run(debug = True)