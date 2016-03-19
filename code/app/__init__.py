from flask import Flask
from flask.ext.cache import Cache
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.config.from_object('config')

# app.debug = True

toolbar = DebugToolbarExtension(app)
cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'crico-cache-',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': '6379',
    'CACHE_REDIS_URL': 'redis://localhost:6379'
})
# cache = Cache(app,config={'CACHE_TYPE': 'simple'})

from app import views
