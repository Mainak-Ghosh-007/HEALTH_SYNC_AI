from flask import Flask, render_template, jsonify, session
from app.config import Config
from app.extensions import db
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.api import api_bp
from app.services.seed import seed_database
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Add Python builtins and custom filters to Jinja environment
    app.jinja_env.globals.update(max=max, min=min)
    app.jinja_env.filters['format'] = lambda val: f"{int(val):,}" if isinstance(val, (int, float)) or (isinstance(val, str) and val.isdigit()) else str(val)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        if hasattr(app, 'request') or True:
            from flask import request
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'error': 'API endpoint not found'}), 404
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        from flask import request
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Internal server error'}), 500
        return render_template('404.html', error="500 - Internal Server Error"), 500

    # Context processors for all Jinja2 templates
    @app.context_processor
    def inject_global_template_data():
        return {
            'current_user_name': session.get('user_name', 'National Officer'),
            'current_user_role': session.get('user_role', 'OFFICER'),
            'current_user_email': session.get('user_email', 'admin@healthsync.gov'),
            'is_authenticated': 'user_id' in session
        }

    # Automatically create tables and seed demo data on first start
    with app.app_context():
        db.create_all()
        seed_database()

    return app
