from app.modules.community.models import Community
from core.repositories.BaseRepository import BaseRepository


class CommunityRepository(BaseRepository):
    def __init__(self):
        super().__init__(Community)

    def get_all(self):
        return Community.query.all()
