from app import db


class FakeNodo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    doi = db.Column(db.String(255), nullable=False)
