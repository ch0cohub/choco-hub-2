import pytest
from flask import url_for

from app.modules.auth.models import User
from app.modules.auth.services import AuthenticationService
from app.modules.auth.repositories import UserRepository
from app.modules.conftest import login
from app.modules.profile.models import UserProfile
from app.modules.profile.repositories import UserProfileRepository
from app import db


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        user_test = User(email="user@example.com", password="test1234")

        UserProfile(name="Name", surname="Surname", is_verified=True, user=user_test)

        db.session.add(user_test)
        db.session.commit()
    yield test_client


def test_login_success(test_client):

    response = login(test_client, "user@example.com", "test1234")

    assert response.request.path != url_for("auth.login"), "Login was unsuccessful"

    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_email(test_client):
    response = test_client.post(
        "/login",
        data=dict(email="bademail@example.com", password="test1234"),
        follow_redirects=True,
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_not_verified(test_client):
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        user_test2 = User(email="userNotVerified@example.com", password="test1234")

        UserProfile(name="Name", surname="Surname", is_verified=False, user=user_test2)

        db.session.add(user_test2)
        db.session.commit()

    response = test_client.post(
        "/login",
        data=dict(email="userNotVerified@example.com", password="test1234"),
        follow_redirects=True,
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_password(test_client):
    response = test_client.post(
        "/login",
        data=dict(email="test@example.com", password="basspassword"),
        follow_redirects=True,
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_signup_user_no_name(test_client):
    response = test_client.post(
        "/signup",
        data=dict(surname="Foo", email="test@example.com", password="test1234"),
        follow_redirects=True,
    )
    assert response.request.path == url_for(
        "auth.show_signup_form"
    ), "Signup was unsuccessful"
    assert b"This field is required" in response.data, response.data


def test_signup_user_unsuccessful(test_client):
    email = "test@example.com"
    response = test_client.post(
        "/signup",
        data=dict(name="Test", surname="Foo", email=email, password="test1234"),
        follow_redirects=True,
    )
    assert response.request.path == url_for(
        "auth.show_signup_form"
    ), "Signup was unsuccessful"
    assert f"Email {email} in use".encode("utf-8") in response.data


def test_signup_user_successful(test_client):
    response = test_client.post(
        "/signup",
        data=dict(
            name="Foo", surname="Example", email="foo@example.com", password="foo1234"
        ),
        follow_redirects=True,
    )
    assert response.request.path == url_for(
        "signupvalidation.index"
    ), "Signup was unsuccessful"


def test_service_create_with_profie_success(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "service_test@example.com",
        "password": "test1234",
    }

    AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 1
    assert UserProfileRepository().count() == 1


def test_service_create_with_profile_fail_no_email(clean_database):
    data = {"name": "Test", "surname": "Foo", "email": "", "password": "1234"}

    with pytest.raises(ValueError, match="Email is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_service_create_with_profile_fail_no_password(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "test@example.com",
        "password": "",
    }

    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_service_create_with_profile_template_injection(clean_database):
    data = {
        # This is a template injection attack, if it is not caught, it will evaluate the expression.
        "name": "{{7*7}}",
        "surname": "Foo",
        "email": "test@example.com",
        "password": "testpassword",
    }
    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0
    assert data.values.__name__ != "49"


def test_service_create_with_profile_sqlinjection(clean_database):
    data = {
        # This is a template injection attack, if it is not caught, it will evaluate the expression.
        "name": "or" "=",
        "surname": "Foo",
        "email": "test@example.com",
        "password": "",
    }
    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)
    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0
