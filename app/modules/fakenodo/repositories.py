from app.modules.fakenodo.models import FakeNodo
from core.repositories.BaseRepository import BaseRepository


class FakeNodoRepository(BaseRepository):
    def __init__(self):
        super().__init__(FakeNodo)
