from app.modules.explore.repositories import ExploreRepository
from core.services.BaseService import BaseService


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(self, search_criteria, **kwargs):
        print("search criteria desde service", search_criteria)
        return self.repository.filter(search_criteria, **kwargs)
