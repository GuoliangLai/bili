from media import baseMedia
from media import media_data_path
import os
import sqlite3
from simple_logger import logging_
log = logging_('./log.log').logger



class biliResource(baseMedia):
    def __init__(self, title, url, time, nfo, actors, meta=None, flag=None):
        super().__init__(title, url, time, nfo, actors, meta, flag)

    def from_title_get_url(self, title):
        return super().form_title_get_src(title)

    def from_url_get_title(self, url):
        return super().form_title_get_src(url)


