from app import db
from app.modules.fakenodo.models import Deposition
import json


def seed_deposition():

    depositions = [
        Deposition(
            status="draft",
            doi="10.1234/example-doi-1",
            dep_metadata=json.dumps(
                {
                    "title": "Example Title 1",
                    "description": "This is a sample metadata for deposition 1.",
                    "authors": ["Author A", "Author B"],
                    "date": "2024-12-06",
                }
            ),
        ),
        Deposition(
            status="published",
            doi="10.1234/example-doi-2",
            dep_metadata=json.dumps(
                {
                    "title": "Example Title 2",
                    "description": "This is a sample metadata for deposition 2.",
                    "authors": ["Author C"],
                    "date": "2024-12-05",
                }
            ),
        ),
        Deposition(
            status="draft",
            doi=None,
            dep_metadata=json.dumps(
                {
                    "title": "Example Title 3",
                    "description": "This deposition has no DOI assigned yet.",
                    "authors": ["Author D", "Author E"],
                    "date": "2024-12-04",
                }
            ),
        ),
    ]

    for deposition in depositions:
        db.session.add(deposition)

    db.session.commit()
    print("Deposition table seeded successfully!")
