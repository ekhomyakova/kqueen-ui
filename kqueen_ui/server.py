from flask import Flask
from flask import redirect
from flask import url_for
from flask.ext.babel import Babel
from kqueen_ui.blueprints.registration.views import registration
from kqueen_ui.blueprints.ui.views import ui
from werkzeug.contrib.cache import SimpleCache

import logging
import os

logger = logging.getLogger(__name__)

cache = SimpleCache()

config_file = os.environ.get('KQUEEN_CONFIG_FILE', 'config/dev.py')


def create_app(config_file=config_file):
    app = Flask(__name__, static_folder='./asset/static')

    app.register_blueprint(ui, url_prefix='/ui')
    app.register_blueprint(registration, url_prefix='/registration')

    # load configuration
    if app.config.from_pyfile(config_file):
        logger.info('Loading configuration from {}'.format(config_file))
    else:
        raise Exception('Config file {} could not be loaded.'.format(config_file))

    # allow override of backend urls from env variables
    kqueen_api_url = os.getenv('KQUEEN_API_URL', app.config['KQUEEN_API_URL'])
    kqueen_auth_url = os.getenv('KQUEEN_AUTH_URL', app.config['KQUEEN_AUTH_URL'])
    app.config.update(
        KQUEEN_API_URL=kqueen_api_url,
        KQUEEN_AUTH_URL=kqueen_auth_url
    )
    Babel(app)
    return app


app = create_app()
app.logger.setLevel(logging.INFO)


@app.route('/')
def root():
    return redirect(url_for('ui.index'), code=302)


def run():
    logger.debug('kqueen_ui starting')
    app.run(port=8000)
