"""
AgriSmart AI — Flask Extensions
=================================
All Flask extension instances created here (not initialized yet).
Actual initialization happens in the app factory via init_app().
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address, default_limits=["100000 per day", "10000 per hour"])
cors = CORS()
