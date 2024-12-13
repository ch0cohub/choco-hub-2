import logging
import random
import string
from flask import jsonify, Response

from app.modules.fakenodo.repositories import FakeNodoRepository
from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)


class FakeNodoService(BaseService):

    def __init__(self):
        super().__init__(FakeNodoRepository())

    def test_full_connection(self) -> Response:
        """
        Simulate testing connection with FakeNodo.
        """
        logger.info("Simulating connection to FakeNodo...")
        return jsonify(
            {"success": True, "message": "FakeNodo connection test successful."}
        )

    def create_new_deposition(self, title: str, description: str) -> dict:
        """
        Simulate creating a new deposition.
        """
        logger.info("Simulating deposition creation on FakeNodo...")

        fake_doi = "10.1234/" + "".join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )

        deposition = {
            "id": random.randint(1000, 9999),
            "title": title,
            "description": description,
            "doi": fake_doi,
        }

        logger.info(f"Fake deposition created: {deposition}")
        return deposition

    def upload_file(self, deposition_id: int, filename: str) -> dict:
        """
        Simulate uploading a file to a deposition.
        """
        logger.info(
            f"Simulating file upload to deposition {deposition_id} on FakeNodo..."
        )
        return {
            "success": True,
            "message": f"File '{filename}' simulated as uploaded to deposition {deposition_id}",
        }

    def publish_deposition(self, deposition_id: int) -> dict:
        """
        Simulate publishing a deposition.
        """
        logger.info(f"Simulating publishing deposition {deposition_id} on FakeNodo...")
        return {
            "success": True,
            "message": f"Deposition {deposition_id} simulated as published.",
        }
