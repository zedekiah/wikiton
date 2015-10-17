# -*- coding: utf8 -*-
from sqlite3 import connect
import json


class WikiDB(object):
    def __init__(self):
        with open("settings.json") as fd:
            self.config = json.load(fd)["db"]
        self.conn = connect(self.config["path"])

    def close(self):
        self.conn.close()

    def query(self, sql, params=tuple()):
        """Method for SELECT queries. Returns cursor object.

        :param sql: str
        :param params: tuple|list
        """
        c = self.conn.cursor()
        c.execute(sql, params)
        return c

    def execute(self, sql, params=tuple()):
        """Method for UPDATE, INSERT and DELETE queries.

        :param sql:
        :param params:
        :return: None
        """
        self.query(sql, params)
        self.conn.commit()

    def execute_script(self, sql_script):
        self.conn.executescript(sql_script)

    def get_page(self, path, lang=None):
        if lang is None:
            lang = self.get_option('default_lang', 'en')
        cur = self.query("SELECT id, lang, path, title, content "
                         "FROM pages "
                         "WHERE path = ? AND lang = ?",
                         (path, lang))
        page = cur.fetchone()
        if page:
            return {"id": page[0],
                    'lang': page[1],
                    "path": page[2],
                    "title": page[3],
                    "content": page[4]}

    def add_page(self, lang, path, title, content):
        self.execute("INSERT INTO pages (lang, path, title, content) "
                     "VALUES (?, ?, ?, ?)", (lang, path, title, content))

    def update_page(self, page_id, title, content):
        self.execute("UPDATE pages SET title = ?, content = ? WHERE id = ?",
                     (title, content, page_id))

    def move_page(self, page_id, new_path):
        self.execute("UPDATE pages SET path = ? WHERE id = ?",
                     (new_path, page_id))

    def delete_page(self, path):
        self.execute("DELETE FROM pages WHERE path = ?", (path, ))

    def get_main_page(self, lang=None):
        page_path = self.get_option('main_page') or 'main'
        lang = lang or self.get_option('default_lang', 'en')
        p = self.get_page(page_path, lang) or {'path': page_path, 'lang': lang}
        return p

    def get_option(self, name, default=None):
        c = self.query('SELECT value FROM options WHERE name = ?', (name, ))
        r = c.fetchone()
        return r[0] if r else default

    def get_options(self):
        c = self.query('SELECT name, value FROM options ORDER BY name')
        return [{'name': r[0], 'value': r[1]} for r in c]

    def set_option(self, name, value):
        self.execute('INSERT OR REPLACE INTO options (name, value) '
                     'VALUES (?, ?)', (name, value))