import pytest
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from flask_login import current_user

@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

    yield test_client
    
@pytest.fixture(scope="module")
def test_client_not_logged_in(test_client):
    """
    Returns a test client without a logged-in user.
    """
    logout(test_client)
    yield test_client

def test_login_logout_flow(test_client):
    """
    Test logging in and out using the auth module.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    assert current_user.is_authenticated, "The user is not authenticated after login."

    # Log out the test user
    logout_response = logout(test_client)
    assert logout_response.status_code == 200, "Logout was unsuccessful."
    assert not current_user.is_authenticated, "The user is still authenticated after logout."

def test_registration(test_client):
    """
    Test the registration process.
    """
    response = test_client.post('/signup/', data={
        'email': 'newuser@example.com',
        'password': 'newpassword123',
        'confirm_password': 'newpassword12'
    }, follow_redirects=True)
    
    assert response.status_code == 200, "Registration failed."
    with test_client.application.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is None, "New user was not created in the database."

def test_protected_route_access(test_client, test_client_not_logged_in):
    """
    Test that a protected route is inaccessible without logging in and accessible after logging in.
    """
    # Ensure the user is logged out before attempting to access the protected route
    logout(test_client)
    response = test_client_not_logged_in.get('/dataset/list', follow_redirects=False)
    assert response.status_code == 302, "Protected route should not be accessible without logging in."

    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    assert current_user.is_authenticated, "The user should be authenticated after login."

    # Attempt to access protected route after login
    response = test_client.get('/dataset/list', follow_redirects=True)
    assert response.status_code == 200, "Protected route should be accessible after logging in."

    # Log out the user after test
    logout_response = logout(test_client)
    assert logout_response.status_code == 200, "Logout was unsuccessful."
    assert not current_user.is_authenticated, "The user is still authenticated after logout."