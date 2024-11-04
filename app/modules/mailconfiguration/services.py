import os

from dotenv import load_dotenv
from flask_mail import Mail, Message
from app.modules.mailconfiguration.repositories import MailconfigurationRepository
from core.services.BaseService import BaseService

load_dotenv()


class MailconfigurationService(BaseService):
    def __init__(self):
        super().__init__(MailconfigurationRepository())
        self.mail = None
        self.sender = None

    def init_app(self, app):
        app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
        app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', '587'))
        app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
        app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
        app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'example@gmail.com')
        app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'example')
        app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

        self.mail = Mail(app)
        self.sender = app.config['MAIL_USERNAME']

    def send_email(self, subject, recipients, body, html_body=None):
        msg = Message(subject, sender=self.sender, recipients=recipients)
        msg.body = body
        if html_body:
            msg.html = html_body

        self.mail.send(msg)
