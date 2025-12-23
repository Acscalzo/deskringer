from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os

# Import db from models
from models import db

# Initialize other extensions
jwt = JWTManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')

    # Disable strict trailing slashes (allow both /api/endpoint and /api/endpoint/)
    app.url_map.strict_slashes = False

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})  # Configure properly for production

    # Import models (needed for migrations) - must be after db.init_app
    with app.app_context():
        from models import Admin, Customer, Call, CallLog

    # Register blueprints
    from routes.admin import admin_bp
    from routes.customers import customers_bp
    from routes.calls import calls_bp
    from routes.webhooks import webhooks_bp
    from routes.stripe_admin import stripe_admin_bp

    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(calls_bp, url_prefix='/api/calls')
    app.register_blueprint(webhooks_bp, url_prefix='/api/webhooks')
    app.register_blueprint(stripe_admin_bp, url_prefix='/api/stripe')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}, 200

    @app.route('/')
    def index():
        return {
            'message': 'DeskRinger API',
            'version': '1.0.0',
            'status': 'running'
        }, 200

    return app

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
