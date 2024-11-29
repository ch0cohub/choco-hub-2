import pytest
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from flask_login import current_user

@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client

def test_integration_profile_summary_access(test_client):
    """
    Test accessing the profile summary page.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/summary")
    assert response.status_code == 200, "The profile summary page could not be accessed."
    assert b"Summary" in response.data or b"Datasets" in response.data, "The expected content is not present on the page"

    logout(test_client)

def test_profile_edit_integration(test_client):
    """
    Test editing the profile information via the integration test.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post(
        "/profile/edit",
        data=dict(
            name="UpdatedName",
            surname="UpdatedSurname",
            orcid="0000-0001-0020-0330",
            affiliation="UpdatedAffiliation"
        ),
        follow_redirects=True
    )
    assert response.status_code == 200, "Profile update failed."
    assert b"Profile updated" in response.data or b"successfully" in response.data, "Profile update success message not found."

    logout(test_client)

def test_profile_edit_integration_invalid_orcid(test_client):
    """
    Test editing the profile with an invalid ORCID.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post(
        "/profile/edit",
        data=dict(
            name="UpdatedName",
            surname="UpdatedSurname",
            orcid="invalid-orcid",
            affiliation="UpdatedAffiliation"
        ),
        follow_redirects=True
    )
    assert response.status_code == 200, "Profile update with invalid ORCID failed unexpectedly."
    assert b"Invalid" in response.data or b"ORCID" in response.data, "Expected validation error for ORCID not found."

    # Log out the user
    logout(test_client)

def test_profile_edit_integration_long_name(test_client):
    """
    Test editing the profile with an excessively long name or surname.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Edit profile information with long name and surname
    response = test_client.post(
        "/profile/edit",
        data=dict(
            name="JonathanChristopherEdwardAlexanderBenjaminWilliamJamesHenryNicholasMatthewJosephDanielBenjaminFrederickGeorgeTheodoreChristopher",
            surname="AndersonJohnsonRobertsonWilliamsonThompsonHendersonRichardsonAlexanderDavidsonHarrisonRobinsonSandersonPetersonMcDonald",
            orcid="0000-0001-0010-0300",
            affiliation="UpdatedAffiliation"
        ),
        follow_redirects=True
    )
    assert response.status_code == 200, "Profile update with long name or surname failed unexpectedly."
    assert b"too long" in response.data or b"validation" in response.data, "Expected validation error for name or surname not found."

    # Log out the user
    logout(test_client)

def test_user_datasets_access(test_client):
    """
    Test accessing the datasets of a specific user.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Access user's datasets page
    response = test_client.get(f"/profile/{current_user.profile.id}/datasets")
    assert response.status_code == 200, "The user datasets page could not be accessed."
    assert b"Datasets" in response.data or b"No datasets" in response.data, "The expected content is not present on the datasets page"

    # Log out the user
    logout(test_client)
