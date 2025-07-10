from flask import Flask
from flask_wtf.csrf import CSRFProtect
from extensions import csrf, assets
from config import Config
from routes import register_routes

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    csrf.init_app(app)
    assets.init_app(app)

    # SCSS Bundle (optional)
    from flask_assets import Bundle
    scss = Bundle('style.scss', filters='libsass', output='style.css')
    assets.register('scss_all', scss)

    # Register blueprints/routes
    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
