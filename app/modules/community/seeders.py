from app.modules.community.models import Community
from core.seeders.BaseSeeder import BaseSeeder
from app.modules.auth.models import User



class CommunitySeeder(BaseSeeder):
    priority = 2  # Lower priority

    def run(self):

        user1 = User.query.filter_by(email='user1@example.com').first()
        user2 = User.query.filter_by(email='user2@example.com').first()
        
        if not user1 or not user2:
            raise Exception("Users not found. Please seed users first.")

        
        communityData = [
            # Create any Model object you want to make seed
            Community(id=1,
                      name= "Comunidad de ciencias",
                      description="Una comunidad de ciencias sin más",
                      owner_id= user1.id)
        ]

        self.seed(communityData)
