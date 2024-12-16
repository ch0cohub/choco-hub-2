from app import db


class Signupvalidation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
