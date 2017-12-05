from .config import current_config

from flask import Flask, redirect, request, url_for
from flask.ext.babel import Babel
from kqueen_ui.blueprints.registration.views import registration
from kqueen_ui.blueprints.ui.views import ui
from kqueen_ui.utils.filters import filters
from urllib.parse import urlsplit
from werkzeug.contrib.cache import SimpleCache

import logging

logger = logging.getLogger(__name__)

cache = SimpleCache()


def create_app(config_file=None):
    app = Flask(__name__, static_folder='./asset/static')

    app.register_blueprint(ui, url_prefix='/ui')
    app.register_blueprint(registration, url_prefix='/registration')

    # load configuration
    config = current_config(config_file)
    app.config.from_mapping(config.to_dict())
    app.logger.setLevel(getattr(logging, app.config.get('LOG_LEVEL')))
    app.logger.info('Loading configuration from {}'.format(config.source_file))

    Babel(app)

    app.jinja_env.filters.update(filters)

    return app


app = create_app()


@app.route('/')
def root():
    return redirect(url_for('ui.index'), code=302)


@app.context_processor
def base_url():
    base_url = urlsplit(request.url).scheme + '://' + urlsplit(request.url).netloc
    return dict(base_url=base_url)


def run():
    logger.debug('kqueen_ui starting')
    app.run(
        host=app.config.get('HOST'),
        port=int(app.config.get('PORT'))
    )
