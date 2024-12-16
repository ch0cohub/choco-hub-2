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


def test_forgot_password_flow(test_client):
    """
    Simula el envío del formulario de 'Olvidé mi contraseña' y verifica el flujo completo.
    """
    user_email = "testuser@gmail.com"

    # Enviar una solicitud POST simulando el formulario
    response = test_client.post(
        "/forgot/password",
        data={"email": user_email},
        follow_redirects=True,  # Seguir la redirección automáticamente
    )

    # Verificar que la redirección fue exitosa
    assert response.status_code == 200

    # Verificar que la respuesta final contiene el mensaje esperado (en la página de login)
    assert (
        b"Check your email for the instructions to change your password"
        in response.data
    )


def test_access_reset_password_page(test_client):
    """
    Simula el acceso a la página de cambio de contraseña con un token válido.
    """
    user_email = "testuser@gmail.com"
    # Generar un token válido
    password_service = PasswordService()
    token = password_service.get_token_from_email(user_email)

    # Acceder a la página con el token
    response = test_client.get(f"/change/password/{token}")

    # Verificar que el servidor responde correctamente
    assert response.status_code == 200
    assert b"New password" in response.data
    assert b"Confirm new password" in response.data


def test_change_password_success(test_client):
    """
    Simula el cambio exitoso de contraseña usando un token válido.
    """
    user_email = "testuser@gmail.com"
    new_password = "newsecurepassword"

    # Generar un token válido
    password_service = PasswordService()
    token = password_service.get_token_from_email(user_email)

    # Enviar el formulario con la nueva contraseña
    response = test_client.post(
        f"/change/password/{token}",
        data={"password": new_password, "confirm_password": new_password},
        follow_redirects=True,
    )

    # Verificar redirección al login con mensaje de éxito
    assert response.status_code == 200
    assert b"Your password has been updated!" in response.data


def test_change_password_with_non_matching_passwords(test_client):
    """
    Simula un intento de cambiar la contraseña con contraseñas que no coinciden.
    """
    # Crear un token válido para el test
    password_service = PasswordService()
    valid_token = password_service.get_token_from_email("testuser@gmail.com")

    # Enviar las contraseñas que no coinciden
    response = test_client.post(
        f"/change/password/{valid_token}",
        data={"password": "newpassword123", "confirm_password": "differentpassword123"},
    )

    # Verificar que el servidor no redirige al login y muestra el mensaje de error
    assert response.status_code == 200  # Asegurarse de que no redirige
    assert (
        b'id="submit_button" disabled' in response.data
    )  # Verificar que el botón está deshabilitado


def test_login_with_old_password_failure(test_client):
    """
    Intenta iniciar sesión con la contraseña antigua después del cambio de contraseña.
    """
    user_email = "testuser@gmail.com"
    # Cambiar la contraseña
    password_service = PasswordService()
    password_service.change_password(user_email, "NewPassword123!")

    # Intentar iniciar sesión con la contraseña antigua
    response = test_client.post(
        "/login", data={"email": user_email, "password": "OldPassword123!"}
    )

    # Verificar que el login falle
    assert response.status_code == 200
    assert (
        b"Invalid credentials" in response.data
    )  # Mensaje esperado en la pantalla de login


def test_login_with_new_password_(test_client):
    """
    Intenta iniciar sesión con la contraseña nueva después del cambio de contraseña.
    """
    user_email = "testuser@gmail.com"
    # Cambiar la contraseña
    password_service = PasswordService()
    password_service.change_password(user_email, "NewPassword123!")

    # Intentar iniciar sesión con la contraseña nueva
    response = test_client.post(
        "/login", data={"email": user_email, "password": "NewPassword123!"}
    )

    # Verificar que el login sea exitoso y redirija
    assert response.status_code == 302
    assert response.headers["Location"] == url_for("public.index")
