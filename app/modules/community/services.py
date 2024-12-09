from app.modules.community.repositories import CommunityRepository
from core.services.BaseService import BaseService
from app.modules.community.models import Community


class CommunityService(BaseService):
    def __init__(self):
        super().__init__(CommunityRepository())

    def get_all(self) -> Community:
        return self.repository.get_all()