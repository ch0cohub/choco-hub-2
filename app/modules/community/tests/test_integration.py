import pytest
from flask_login import current_user
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.community.models import Community
from app.modules.community.services import CommunityService
from app.modules.profile.models import UserProfile

def setup_test_data():
    """Helper function to create test data."""
    # Eliminar datos existentes para evitar conflictos
    User.query.delete()
    UserProfile.query.delete()
    Community.query.delete()
    db.session.commit()

    # Crear usuario principal
    user = User(email="testuser@example.com", password="testpassword")
    profile = UserProfile(name="Test", surname="User", is_verified=True, user=user)
    db.session.add(user)
    db.session.add(profile)
    db.session.commit()

    # Crear comunidad
    community_service = CommunityService()
    community = community_service.create(
        name="Test Community", 
        description="This is a test community.", 
        owner_id=user.id
    )

    # Crear otro usuario no propietario
    other_user = User(email="otheruser@example.com", password="otherpassword")
    profile_other = UserProfile(name="Other", surname="User", is_verified=True, user=other_user)
    db.session.add(other_user)
    db.session.add(profile_other)
    db.session.commit()

    return user, other_user



@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        setup_test_data()
    yield test_client

def test_index(test_client):
    """Test the index route for communities."""
    with test_client.application.app_context():
        community = Community.query.filter_by(name="Test Community").first()
        assert community, "Test Community was not found in the database."

    response = test_client.get("/community")
    assert response.status_code == 200, "Index page is not accessible."
    assert b"Test Community" in response.data, "Community name is not displayed."


def test_create_community(test_client):
    """Test creating a new community."""
    login_response = login(test_client, "testuser@example.com", "testpassword")
    assert login_response.status_code == 200, "Login failed."

    response = test_client.post(
        "/community/create",
        data={"name": "New Community", "description": "This is another test community."},
        follow_redirects=True
    )
    assert response.status_code == 200, "Community creation failed."

    logout(test_client)


def test_get_community(test_client):
    """Test viewing a specific community by ID."""
    login_response = login(test_client, "testuser@example.com", "testpassword")
    assert login_response.status_code == 200, "Login failed."

    with test_client.application.app_context():
        community = Community.query.filter_by(name="Test Community").first()
        assert community, "Test Community was not found."

    response = test_client.get(f"/community/{community.id}")
    assert response.status_code == 200, "Community detail page is not accessible."
    assert b"This is a test community." in response.data, "Community description was not displayed."

    logout(test_client)

def test_join_community(test_client):
    """Test joining a community."""
    
    login_response = login(test_client, "otheruser@example.com", "otherpassword")
    assert login_response.status_code == 200, "Login failed."

    with test_client.application.app_context():
        
        community = Community.query.filter_by(name="Test Community").first()
        assert community, "Test Community was not found in the database."

        other_user = User.query.filter_by(email="otheruser@example.com").first()
        assert other_user not in community.members, "User is already a member of the community."


    response = test_client.post(
        "/community/join",
        json={"community_id": community.id}
    )
    assert response.status_code == 200, "Failed to join the community."
   

    with test_client.application.app_context():
        
        community = Community.query.get(community.id)  
        assert other_user in community.members, "User was not added to the community."

    logout(test_client)


def test_leave_community(test_client):
    """Test leaving a community."""

    login_response = login(test_client, "otheruser@example.com", "otherpassword")
    assert login_response.status_code == 200, "Login failed."

    with test_client.application.app_context():

        community = Community.query.filter_by(name="Test Community").first()
        assert community, "Test Community was not found in the database."


        other_user = User.query.filter_by(email="otheruser@example.com").first()
        if other_user not in community.members:

            community.members.append(other_user)
            db.session.commit()
        

        assert other_user in community.members, "User is not a member of the community."


    response = test_client.post(
        "/community/leave",
        json={"community_id": community.id}
    )
    assert response.status_code == 200, "Failed to leave the community."
    assert b"You have successfully left the community" in response.data, "Success message not found in response."

    with test_client.application.app_context():

        community = Community.query.get(community.id)
        assert other_user not in community.members, "User was not removed from the community."


    logout(test_client)




def test_edit_community(test_client):
    """Test editing a community."""
    login_response = login(test_client, "testuser@example.com", "testpassword")
    assert login_response.status_code == 200, "Login failed."

    with test_client.application.app_context():
        community = Community.query.filter_by(name="Test Community").first()
        assert community, "Test Community was not found."

    response = test_client.post(
        f"/community/edit/{community.id}",
        data={"name": "Updated Community", "description": "Updated description."},
        follow_redirects=True
    )
    assert response.status_code == 200, "Community edit failed."
    assert b"Updated Community" in response.data, "Updated community name is not displayed."

    with test_client.application.app_context():
        updated_community = Community.query.get(community.id)
        assert updated_community.name == "Updated Community", "Community name was not updated."

    logout(test_client)
    
    
def test_delete_community(test_client):
    """Test deleting a community."""
    login_response = login(test_client, "testuser@example.com", "testpassword")
    assert login_response.status_code == 200, "Login failed."

    with test_client.application.app_context():
        community = Community.query.filter_by(name="Updated Community").first()
        assert community, "Community to delete was not found."

    response = test_client.post(f"/community/delete/{community.id}", follow_redirects=True)
    assert response.status_code == 200, "Community deletion failed."

    with test_client.application.app_context():
        deleted_community = Community.query.get(community.id)
        assert deleted_community is None, "Community was not deleted."

    logout(test_client)
    
    
