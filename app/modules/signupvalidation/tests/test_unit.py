import pytest
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app import db
from app.modules.signupvalidation.services import SignupvalidationService


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Crear dos usuarios de prueba
        user1 = User(email="user1@example.com", password="password1")
        user2 = User(email="user2@example.com", password="password2")

        # Crear perfiles para ambos usuarios
        profile1 = UserProfile(
            name="User", surname="One", is_verified=False, user=user1
        )
        profile2 = UserProfile(
            name="User", surname="Two", is_verified=False, user=user2
        )

        # Agregar usuarios y perfiles a la base de datos
        db.session.add_all([user1, user2, profile1, profile2])
        db.session.commit()

    yield test_client


def test_unique_confirmation_links(test_client):
    """
    Verifica que los enlaces de confirmación generados para dos usuarios sean únicos.
    """
    signup_service = SignupvalidationService()

    link1 = signup_service.get_token_from_email("user1@example.com")
    link2 = signup_service.get_token_from_email("user2@example.com")

    assert (
        link1 != link2
    ), "Los enlaces de confirmación generados para los usuarios no son únicos."

    serializer = signup_service.get_serializer()
    email1 = serializer.loads(link1, salt=signup_service.CONFIRM_EMAIL_SALT)
    email2 = serializer.loads(link2, salt=signup_service.CONFIRM_EMAIL_SALT)

    assert (
        email1 == "user1@example.com"
    ), "El enlace generado no corresponde al primer usuario."
    assert (
        email2 == "user2@example.com"
    ), "El enlace generado no corresponde al segundo usuario."


def test_confirm_user_with_valid_token(test_client):
    signup_service = SignupvalidationService()

    # Generacion de url
    token = signup_service.get_token_from_email("user1@example.com")

    user = signup_service.confirm_user_with_token(token)

    assert (
        user.profile.is_verified == True
    ), "El usuario no fue confirmado correctamente."


def test_duplicate_confirmation_link(test_client):
    signup_service = SignupvalidationService()

    link1 = signup_service.get_token_from_email("user1@example.com")
    link2 = signup_service.get_token_from_email("user1@example.com")

    assert (
        link1 == link2
    ), "Los enlaces generados para el mismo usuario deberían ser iguales."
