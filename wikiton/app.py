# -*- coding: utf8 -*-
from flask import Flask
import json


app = Flask('Wikiton')
with open('settings.json') as fd:
    app.config.update(json.load(fd))
