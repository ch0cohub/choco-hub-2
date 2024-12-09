from flask import render_template
from flask_login import current_user, login_required
from app.modules.community import community_bp
from app.modules.community.forms import CommunityForm
from app.modules.community.services import CommunityService

community_service = CommunityService()
@community_bp.route('/community', methods=['GET'])
def index():
    communities = community_service.get_all()
    return render_template('community/index.html', communities=communities)

'''
CREATE
'''
@community_bp.route('/community/create', methods=['GET', 'POST'])
@login_required
def create_community():
    form = CommunityForm()
    if form.validate_on_submit():
        result = community_service.create(name=form.name.data, description=form.description.data, owner_id=current_user.id)
        return community_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='community.index',
            success_msg='Community created successfully!',
            error_template='community/create.html',
            form=form
        )
    return render_template('community/create.html', form=form)
