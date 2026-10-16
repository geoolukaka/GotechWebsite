"""
GoTech Solutions - Contact Form Backend
========================================
A small Flask API that receives contact-form submissions from the website
and stores them in either Google Sheets or MySQL, depending on the
STORAGE_BACKEND setting in your .env file.

Run locally:
    pip install -r requirements.txt
    cp .env.example .env      # then fill in the values
    python app.py

The API exposes:
    POST /api/contact   -> validates + stores a submission
    GET  /api/health     -> simple health check
    GET  /api/submissions (optional, protected by API key) -> list recent submissions

See README.md for full setup instructions (Google Sheets AND MySQL).
"""

import logging
import os
import threading
import time
from collections import defaultdict, deque

from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from notifiers import get_notifier
from notifiers.whatsapp import NotificationError
from storage import get_storage_backend
from validation import ValidationError, validate_submission

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gotech.backend")


class RateLimiter:
    """Tiny in-memory per-IP limiter so the form can't be used to spam WhatsApp."""

    def __init__(self, max_hits: int, window_seconds: int):
        self.max_hits = max_hits
        self.window = window_seconds
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.time()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] > self.window:
                hits.popleft()
            if len(hits) >= self.max_hits:
                return False
            hits.append(now)
            return True


def create_app(config_object: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Allow the static site (GitHub Pages, localhost, etc.) to call this API.
    allowed_origins = app.config["ALLOWED_ORIGINS"]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

    # Storage backend is chosen once at startup based on STORAGE_BACKEND
    # ("google_sheets" or "mysql") and reused for every request.
    storage = get_storage_backend(app.config)
    app.extensions = getattr(app, "extensions", {})
    app.extensions["storage"] = storage

    # WhatsApp notifier ("callmebot", "cloud_api" or "none") chosen at startup.
    app.extensions["notifier"] = get_notifier(app.config)
    app.extensions["rate_limiter"] = RateLimiter(
        app.config["RATE_LIMIT_MAX"], app.config["RATE_LIMIT_WINDOW_SECONDS"]
    )

    register_routes(app)
    register_error_handlers(app)
    return app


def register_routes(app: Flask) -> None:
    @app.get("/api/health")
    def health():
        return jsonify(
            status="ok",
            backend=app.config["STORAGE_BACKEND"],
            whatsapp=app.config["WHATSAPP_PROVIDER"],
        )

    @app.post("/api/contact")
    def submit_contact():
        storage = app.extensions["storage"]
        notifier = app.extensions["notifier"]

        payload = request.get_json(silent=True) or request.form.to_dict()

        # Honeypot: real visitors never see or fill this field, bots do.
        if str(payload.get("website", "")).strip():
            return jsonify(status="success", id="0"), 201

        ip_address = (request.headers.get("X-Forwarded-For", request.remote_addr) or "").split(",")[0].strip()
        if not app.extensions["rate_limiter"].allow(ip_address):
            return (
                jsonify(status="error",
                        message="Too many messages sent. Please wait a few minutes and try again."),
                429,
            )

        try:
            clean = validate_submission(payload)
        except ValidationError as exc:
            return jsonify(status="error", message=str(exc), field=exc.field), 400

        clean["page"] = clean.get("page") or request.headers.get("Referer", "")
        clean["ip_address"] = ip_address

        # 1) Save the inquiry (a no-op in-memory store when STORAGE_BACKEND=none).
        saved = False
        record_id = None
        try:
            record_id = storage.save_submission(clean)
            saved = storage.durable
        except Exception:
            logger.exception("Failed to persist contact submission")

        # 2) Send it to WhatsApp.
        notified = True
        try:
            notifier.send(clean)
        except NotificationError:
            notified = False
            logger.exception("Failed to send WhatsApp notification")

        whatsapp_on = app.config["WHATSAPP_PROVIDER"] != "none"

        # Success only if the inquiry reached us by at least one durable route:
        # a real database/sheet, or a delivered WhatsApp message.
        if saved or (whatsapp_on and notified):
            logger.info("Inquiry received id=%s from %s (saved=%s, whatsapp=%s)",
                        record_id, clean["email"], saved, notified)
            return jsonify(status="success", id=record_id, whatsapp=notified), 201

        return (
            jsonify(
                status="error",
                message="We could not send your message right now. Please try again shortly or message us on WhatsApp.",
            ),
            502,
        )

    @app.get("/api/submissions")
    def list_submissions():
        # Lightweight protection so this endpoint isn't wide open. Set
        # ADMIN_API_KEY in .env and pass it as X-API-Key to use this.
        api_key = app.config.get("ADMIN_API_KEY")
        if not api_key or request.headers.get("X-API-Key") != api_key:
            return jsonify(status="error", message="Unauthorized"), 401

        storage = app.extensions["storage"]
        limit = min(int(request.args.get("limit", 50)), 500)
        return jsonify(status="success", submissions=storage.list_submissions(limit=limit))


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_err):
        return jsonify(status="error", message="Not found"), 404

    @app.errorhandler(500)
    def server_error(_err):
        return jsonify(status="error", message="Internal server error"), 500


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
