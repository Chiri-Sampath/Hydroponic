"""
AgriSmart AI — Development Entry Point
========================================
Run with:  python run.py
Production uses gunicorn:  gunicorn -w 2 -b 0.0.0.0:$PORT "app:create_app()"
"""

from app import create_app

app = create_app("development")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
