import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from app.routes.tasks import tasks_bp

load_dotenv()


def create_app():
    app = Flask(__name__)

    allowed_origins = [
        "http://localhost:3000",
        "https://frontend-khaki-psi-48.vercel.app"
    ]

    extra_origin = os.getenv("FRONTEND_ORIGIN")
    if extra_origin and extra_origin not in allowed_origins:
        allowed_origins.append(extra_origin)

    CORS(
        app,
        origins=allowed_origins,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PATCH", "OPTIONS"]
    )

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "task-manager-api"
        })

    app.register_blueprint(tasks_bp)

    return app