"""
Main entry point for production deployment.
This file is used by WSGI servers like Gunicorn.
"""
from app import app

if __name__ == "__main__":
    app.run()