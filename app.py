from flask import Flask, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from config import Config
from routes.auth import auth_bp
from routes.books import books_bp
from routes.upload import upload_bp
from routes.extract import extract_bp
from routes.ai import ai_bp
from pathlib import Path
import os
import datetime
import logging
import traceback

# Ensure logs directory exists
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "server.log"

def setup_logging(app):
    handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS (Allow everything for demo)
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # configure file logging for both dev and WSGI use
    setup_logging(app)
    
    # Initialize JWT
    jwt = JWTManager()
    jwt.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(books_bp, url_prefix="/api/books")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")
    app.register_blueprint(extract_bp, url_prefix="/api/extract")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    
    # Import and register new blueprints
    from routes.admin import admin_bp
    from routes.payment import payment_bp
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")

    @app.route("/api/health")
    def health():
        return jsonify({"status":"ok", "time": datetime.datetime.utcnow().isoformat()})

    # Redirect root to UI for better UX
    @app.route("/")
    def index():
        from flask import redirect
        return redirect("/ui")

    # Log exceptions to file for post-mortem
    @app.errorhandler(500)
    def handle_500(err):
        tb = traceback.format_exc()
        app.logger.error("Unhandled exception:\n%s", tb)
        return jsonify({"error":"internal server error"}), 500

    # Serve local uploads (dev)
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        upload_folder = app.config['UPLOAD_FOLDER']
        return send_from_directory(upload_folder, filename, as_attachment=False)
    
    # Serve PDF files for PDF.js rendering
    @app.route("/pdf/<path:filename>")
    def serve_pdf(filename):
        upload_folder = app.config['UPLOAD_FOLDER']
        response = send_from_directory(upload_folder, filename, mimetype='application/pdf', as_attachment=False)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    # Serve the lightweight interactive UI
    ui_dir = Path(__file__).parent / "static_ui"

    @app.route('/ui')
    def ui_index():
        return send_from_directory(str(ui_dir), 'index.html')

    @app.route('/ui/<path:filename>')
    def ui_static(filename):
        return send_from_directory(str(ui_dir), filename)

    return app

# Export a top-level WSGI application for servers (Waitress/gunicorn)
# This allows `waitress-serve --listen=*:5000 app:application` or
# `waitress-serve --call 'app:create_app'` to work reliably.
application = create_app()

if __name__ == "__main__":
    app = create_app()
    # Configure logging to file
    setup_logging(app)
    app.logger.info("Starting Cloud eLibrary Backend")
    # Use threaded mode to handle concurrent requests
    app.run(host="0.0.0.0", port=app.config["PORT"], debug=False, threaded=True)
