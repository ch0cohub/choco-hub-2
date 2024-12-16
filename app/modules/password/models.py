from app import db


class Password(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"Password<{self.id}>"
