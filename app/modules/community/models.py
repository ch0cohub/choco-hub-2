from app import db

user_community = db.Table(
    'user_community',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('community_id', db.Integer, db.ForeignKey('community.id'), primary_key=True)
)
class Community(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    owner = db.relationship('User', backref='owner-community', lazy=True)
    members = db.relationship('User', secondary=user_community, backref=db.backref('joined_communities', lazy='dynamic'))
    
    shared_datasets = db.relationship(
        'DataSet',
        backref='shared_community',
        lazy=True
    )
    
    def __repr__(self):
        return f'Community<{self.id}>'

