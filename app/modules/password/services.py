from dotenv import load_dotenv
from app.modules.password.repositories import PasswordRepository
from core.services.BaseService import BaseService
from app import db
from werkzeug.security import generate_password_hash
from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer
from app.modules.auth.models import User
from app import mail_configuration
import os
load_dotenv()


class PasswordService(BaseService):
    def __init__(self):
        super().__init__(PasswordRepository())
        self.CONFIRM_EMAIL_SALT = os.getenv('CONFIRM_EMAIL_SALT', 'sample_salt')
        self.CONFIRM_EMAIL_TOKEN_MAX_AGE = os.getenv('CONFIRM_EMAIL_TOKEN_MAX_AGE', 3600)

    def get_serializer(self):
        return URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    def get_token_from_email(self, email):
        s = self.get_serializer()
        return s.dumps(email, salt="sample_salt")

    def send_change_password_email(self, password_email):
        token = self.get_token_from_email(password_email)

        user = User.query.filter_by(email=password_email).first()
        if user:
            url = url_for('password.change_password', token=token, _external=True)
            html_body = f"<a href='{url}'>Please confirm your identity</a>"

            mail_configuration.send_email(
                subject="Please confirm your Identity",
                recipients=[password_email],
                body="Please confirm your identity and change your password by clicking the link below.",
                html_body=html_body
            )

    def get_email_by_token(self, token):
        s = self.get_serializer()
        email = s.loads(token, salt='sample_salt', max_age=3600)
        return email

    def change_password(self, email, password):
        new_password = generate_password_hash(password)
        user = User.query.filter_by(email=email).first()
        user.password = new_password
        db.session.commit()
