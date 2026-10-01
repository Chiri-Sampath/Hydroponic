"""
AgriSmart AI — Flask Application Factory
=========================================
Initializes extensions, registers blueprints, and returns the Flask app.
"""

import os
from flask import Flask, jsonify
from .config import config_by_name
from .extensions import db, jwt, migrate, limiter, cors



def create_app(config_name: str = None) -> Flask:
    """Application factory. Creates and configures the Flask app."""

    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Configure CORS for frontend (allows all local dev origins, Live Server, and file/http servers)
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": "*",
                "allow_headers": ["Content-Type", "Authorization"],
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
            }
        },
        supports_credentials=False,
        always_send=True
    )

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Root endpoint for hosting health checks (Render / Uptime monitors)
    @app.route("/", methods=["GET", "HEAD"])
    def root_health():
        return jsonify({
            "status": "online",
            "service": "AgriSmart AI API Engine",
            "version": app.config.get("APP_VERSION", "1.0.0"),
            "health": "/api/health"
        }), 200

    # Register blueprints
    _register_blueprints(app)

    # Global CORS headers on every response
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        return response

    # Register error handlers
    _register_error_handlers(app)

    # Auto-initialize database tables and knowledge base data
    with app.app_context():
        try:
            if app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite"):
                os.makedirs(app.instance_path, exist_ok=True)
            db.create_all()
            from .models.cultivation import Product
            if Product.query.count() == 0:
                from .services.seeder import seed_all_master_data
                seed_all_master_data(db.session)
        except Exception as e:
            app.logger.warning(f"Database auto-init notification: {e}")

    return app


def _register_blueprints(app: Flask) -> None:
    """Register all API route blueprints."""
    from .routes.auth import auth_bp
    from .routes.user import user_bp
    from .routes.buyer import buyer_bp
    from .routes.admin import admin_bp
    from .routes.location import location_bp
    from .routes.weather import weather_bp
    from .routes.cultivation import cultivation_bp
    from .routes.recommendation import recommendation_bp
    from .routes.economics import economics_bp
    from .routes.quality import quality_bp
    from .routes.laboratory import laboratory_bp
    from .routes.market import market_bp
    from .routes.matching import matching_bp
    from .routes.planning import planning_bp
    from .routes.health import health_bp
    from .routes.geocoding import geocoding_bp

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/users")
    app.register_blueprint(buyer_bp, url_prefix="/api/buyer")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(location_bp, url_prefix="/api/location")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")
    app.register_blueprint(cultivation_bp, url_prefix="/api/cultivation")
    app.register_blueprint(recommendation_bp, url_prefix="/api/recommendations")
    app.register_blueprint(economics_bp, url_prefix="/api/economics")
    app.register_blueprint(quality_bp, url_prefix="/api/quality")
    app.register_blueprint(laboratory_bp, url_prefix="/api/labs")
    app.register_blueprint(market_bp, url_prefix="/api/market")
    app.register_blueprint(matching_bp, url_prefix="/api/matching")
    app.register_blueprint(planning_bp, url_prefix="/api/planning")
    app.register_blueprint(
    geocoding_bp,
    url_prefix="/api/geocode"
)


def _register_error_handlers(app: Flask) -> None:
    """Register global error handlers returning consistent JSON."""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"success": False, "error": "Token has expired", "message": "The token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({"success": False, "error": "Invalid token", "message": error_string}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return jsonify({"success": False, "error": "Authorization required", "message": error_string}), 401

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "Bad request", "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "error": "Unauthorized", "message": str(e)}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "error": "Forbidden", "message": str(e)}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Not found", "message": str(e)}), 404

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"success": False, "error": "Unprocessable entity", "message": str(e)}), 422

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"success": False, "error": "Rate limit exceeded", "message": str(e)}), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500
