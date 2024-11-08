from app.modules.signupvalidation.models import Signupvalidation
from core.repositories.BaseRepository import BaseRepository


class SignupvalidationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Signupvalidation)
