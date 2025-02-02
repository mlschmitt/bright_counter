from flask import Flask

from api.routes import api_blueprint


def create_app(test_config=None):
    # Init overall Flask app, register our Blueprints
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY='bright_counter_02022025')

    # Allow config overrides for unit tests
    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('config.py', silent=True)

    app.register_blueprint(api_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=9000)
