from app.modules.password.models import Password
from core.repositories.BaseRepository import BaseRepository


class PasswordRepository(BaseRepository):
    def __init__(self):
        super().__init__(Password)
