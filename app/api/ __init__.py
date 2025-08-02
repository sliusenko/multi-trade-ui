from flask import Flask
from app.api.strategy import strategy_bp


def create_app():
    app = Flask(__name__)

    # інші блупринти
    app.register_blueprint(strategy_bp)

    return app