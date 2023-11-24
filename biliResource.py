from media import baseMedia
from media import media_data_path
import os
import sqlite3


class biliResource(baseMedia):
    def __init__(self, title, url, time, nfo, actors):
        super().__init__(title, url, time, nfo, actors)

    def from_title_get_url(self, title):
        return super().form_title_get_src(title)

    def from_url_get_title(self, url):
        return super().form_title_get_src(url)


