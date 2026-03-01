"""Launcher for Saferpay Explorer - handles PyInstaller frozen paths."""
import sys
import os
import webbrowser
import threading

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

# Set working directory and template/static paths for Flask
base = get_base_path()
os.chdir(base)
os.environ.setdefault('SECRET_KEY', 'saferpay-explorer-local-key')

# Patch Flask to find templates/static in the bundled location
import flask
from app import app

if getattr(sys, 'frozen', False):
    app.template_folder = os.path.join(base, 'templates')
    app.static_folder = os.path.join(base, 'static')

def open_browser():
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n  Saferpay Explorer starting...")
    print(f"  Open: http://localhost:{port}\n")
    threading.Timer(1.5, open_browser).start()
    app.run(host='127.0.0.1', port=port, debug=False)
