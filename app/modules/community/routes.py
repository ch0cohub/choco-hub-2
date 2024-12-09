from flask import render_template
from app.modules.community import community_bp
from app.modules.community.services import CommunityService

community_service = CommunityService()
@community_bp.route('/community', methods=['GET'])
def index():
    communities = community_service.get_all()
    return render_template('community/index.html', communities=communities)
