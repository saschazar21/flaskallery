import os
import jinja_partials
from flask import Flask, g
from werkzeug.middleware.proxy_fix import ProxyFix

from routes import root
from routes.api import api
from db import init_db

app = Flask(__name__)

# Proxy configuration:
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

jinja_partials.register_extensions(app)

app.register_blueprint(root)
app.register_blueprint(api, url_prefix='/api')


@app.teardown_appcontext
def close_db_connection(_exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run()
