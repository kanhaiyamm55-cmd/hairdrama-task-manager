import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from app.routes.tasks import tasks_bp

load_dotenv()


def create_app():
    app = Flask(__name__)

    CORS(
        app,
        origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
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