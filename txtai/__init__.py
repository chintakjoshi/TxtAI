import logging

from dotenv import load_dotenv
from flask import Flask

from txtai.config import load_settings
from txtai.routes.sms import sms_blueprint


def create_app() -> Flask:
    load_dotenv()
    settings = load_settings()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = Flask(__name__)
    app.config["SETTINGS"] = settings
    app.register_blueprint(sms_blueprint)
    return app
