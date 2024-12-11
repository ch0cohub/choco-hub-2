from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from app.modules.community import community_bp
from app.modules.community.forms import CommunityForm
from app.modules.community.models import Community
from app.modules.community.services import CommunityService
from app import db

community_service = CommunityService()
@community_bp.route('/community', methods=['GET'])
def index():
    all_communities = community_service.get_all()

    if current_user.is_authenticated:
        # Clasificar las comunidades si el usuario está autenticado
        owner_communities = [c for c in all_communities if c.owner_id == current_user.id]
        member_communities = [
            c for c in all_communities 
            if c.owner_id != current_user.id and current_user in c.members
        ]
        other_communities = [
            c for c in all_communities 
            if c.owner_id != current_user.id and current_user not in c.members
        ]

        # Combinar las listas para enviarlas al template en el orden deseado
        sorted_communities = owner_communities + member_communities + other_communities
    else:
        # Si el usuario no está autenticado, mostrar todas las comunidades como "otras"
        sorted_communities = all_communities

    return render_template('community/index.html', communities=sorted_communities)



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


'''
DELETE
'''
@community_bp.route('/community/delete/<int:community_id>', methods=['POST'])
@login_required
def delete_community(community_id):
    community = community_service.get_or_404(community_id)

    # Verificar que el usuario sea el propietario
    if community.owner_id != current_user.id:
        flash("You are not allowed to delete this community.", "danger")
        return redirect(url_for('community.index'))

    # Eliminar manualmente las relaciones de miembros
    community.members.clear()
    db.session.commit()

    # Eliminar la comunidad
    db.session.delete(community)
    db.session.commit()
    flash("Community deleted successfully.", "success")
    return redirect(url_for('community.index'))



'''
EDIT
'''
@community_bp.route('/community/edit/<int:community_id>', methods=['GET', 'POST'])
@login_required
def edit_community(community_id):
    community = community_service.get_or_404(community_id)
    if community.owner_id != current_user.id:
        flash('You are not authorized to edit this community', 'error')
        return redirect(url_for('community.index'))

    form = CommunityForm(obj=community)
    if form.validate_on_submit():
        result = community_service.update(
            community_id,
            name=form.name.data,
            description=form.description.data
        )
        return community_service.handle_service_response(
            result=result,
            errors=form.errors,
            success_url_redirect='community.index',
            success_msg='Community updated successfully!',
            error_template='community/edit.html',
            form=form
        )
    return render_template('community/edit.html', form=form, community=community)


'''
READ BY ID
'''
@community_bp.route('/community/<int:community_id>', methods=['GET'])
def get_community(community_id):
    community = community_service.get_or_404(community_id)
    datasets = community.shared_datasets
    
    return render_template('community/show.html', community=community, datasets=datasets)

@community_bp.route('/community/join', methods=['POST'])
@login_required
def join_community():
    community_id = request.json.get('community_id')

    if not community_id:
        return jsonify({'error': 'Community ID is required'}), 400

    community = Community.query.get(community_id)

    if not community:
        return jsonify({'error': 'Community not found'}), 404

    if community.owner_id == current_user.id:
        return jsonify({'error': 'You are the owner of this community'}), 403

    if current_user in community.members:
        return jsonify({'error': 'You are already a member of this community'}), 403

    community.members.append(current_user)
    db.session.commit()

    return jsonify({'message': 'You have successfully joined the community'})

@community_bp.route('/community/leave', methods=['POST'])
@login_required
def leave_community():
    community_id = request.json.get('community_id')
    community = community_service.get_or_404(community_id)

    if not community:
        return jsonify({'error': 'Community not found'}), 404

    if current_user not in community.members:
        return jsonify({'error': 'You are not a member of this community'}), 400

    community.members.remove(current_user)
    db.session.commit()

    return jsonify({'message': 'You have successfully left the community'})
