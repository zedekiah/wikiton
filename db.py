# -*- coding: utf8 -*-
from datetime import datetime
from peewee import *


db = SqliteDatabase('data.db')


class Page(Model):
    lang = CharField(max_length='2')
    path = CharField()
    title = CharField(default='')
    content = TextField(default='')

    class Meta:
        database = db
        db_table = 'pages'

    @classmethod
    def get_main(cls, lang=None):
        if lang is None:
            lang = Option.get_value('default_lang', 'ru')
        path = Option.get_value('main_page', 'main')
        return cls.get(lang=lang, path=path)


class PageHistory(Model):
    page = ForeignKeyField(Page)
    timestamp = DateTimeField()
    title = CharField(default='')
    content = TextField(default='')

    class Meta:
        database = db
        db_table = 'page_history'

    @classmethod
    def create_from_page(cls, page):
        PageHistory.create(page=page, timestamp=datetime.now(),
                           title=page.title, content=page.content)


class Option(Model):
    name = CharField()
    value = CharField()

    class Meta:
        database = db
        db_table = 'options'

    @classmethod
    def set_value(cls, name, value):
        obj, _ = cls.get_or_create(name=name)
        obj.value = value
        obj.save()

    @classmethod
    def get_value(cls, name, default=None):
        val = cls.select(Option.value).where(Option.name == name).scalar()
        return val or default
