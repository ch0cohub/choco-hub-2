from unittest.mock import patch
import pytest
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app import db
from app.modules.password.services import PasswordService
from flask import url_for
from app.modules.conftest import login


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email="testuser@gmail.com", password="Testuser123!")
        UserProfile(user=user_test, name="Test", surname="123", is_verified=True)
        db.session.add(user_test)
        db.session.commit()

    yield test_client


def test_send_change_password_email(test_client):
    """
    Test para verificar que el correo de cambio de contraseña se envía correctamente.
    """
    # Crear una instancia de PasswordService
    password_service = PasswordService()

    # Mockear el método send_email
    with patch("app.mail_configuration.send_email") as mock_send_email:
        # Email ficticio para la prueba
        test_email = "testuser@gmail.com"

        # Crear un contexto de solicitud para que `url_for` funcione
        with test_client.application.test_request_context():
            # Llamar al método que envía el correo
            password_service.send_change_password_email(test_email)

        # Verificar que el método fue llamado una vez
        mock_send_email.assert_called_once()

        # Verificar que los argumentos son correctos
        args, kwargs = mock_send_email.call_args
        assert kwargs["subject"] == "Please confirm your Identity"
        assert kwargs["recipients"] == [test_email]
        assert "Please confirm your identity" in kwargs["body"]
        assert "Please confirm your identity" in kwargs["html_body"]


def test_get_email_by_token(test_client):
    """
    Verifica que el token generado contiene el email correcto.
    """
    password_service = PasswordService()
    user_email = "testuser@gmail.com"
    # Generar token
    token = password_service.get_token_from_email(user_email)

    # Validar token
    email_from_token = password_service.get_email_by_token(token)
    assert email_from_token == user_email


def test_change_password(test_client):
    """
    Verifica que la contraseña se cambie correctamente.
    """
    password_service = PasswordService()

    user_email = "testuser@gmail.com"
    new_password = "NewPassword123!"

    # Cambiar la contraseña
    password_service.change_password(user_email, new_password)

    # Verificar que la contraseña se cambió correctamente
    user = User.query.filter_by(email=user_email).first()
    assert user is not None
    assert user.password != "Testuser123!"  # Verificar que no es la contraseña anterior


def test_login_with_new_password(test_client):
    """
    Verifica que el usuario pueda iniciar sesión con la nueva contraseña.
    """
    password_service = PasswordService()
    user_email = "testuser@gmail.com"
    new_password = "NewPassword123!"

    # Cambiar la contraseña
    password_service.change_password(user_email, new_password)

    # Verificar que la nueva contraseña sea válida
    response = login(test_client, user_email, new_password)
    assert response.request.path != url_for("auth.login"), "Login was unsuccessful"

    assert (
        response.status_code == 200
    ), f"Unexpected status code: {response.status_code}"
    test_client.get("/logout", follow_redirects=True)


def test_login_with_old_password_after_changed(test_client):
    """
    Verifica que el usuario pueda iniciar sesión con la nueva contraseña.
    """
    password_service = PasswordService()
    user_email = "testuser@gmail.com"
    new_password = "NewPassword123!"

    # Cambiar la contraseña
    password_service.change_password(user_email, new_password)

    # Verificar que la nueva contraseña sea válida
    response = test_client.post(
        "/login",
        data=dict(uemail=user_email, password="Testuser123!"),
        follow_redirects=True,
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"
    test_client.get("/logout", follow_redirects=True)
