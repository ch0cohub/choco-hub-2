from locust import HttpUser, TaskSet, task
from flask import Flask
from app.modules.password.services import PasswordService
from core.locust.common import (
    get_csrf_token,
)  # Asegúrate de importar correctamente tu servicio

# Instancia Flask para usar el servicio correctamente
app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"  # Reemplaza con tu llave real


class ChangePasswordBehavior(TaskSet):
    def on_start(self):
        """Ejecutado al inicio de la prueba."""
        self.ensure_logged_out()
        self.login()

    def get_reset_token(self, email):
        """Genera un token válido para el restablecimiento de contraseña."""
        with app.app_context():
            password_service = PasswordService()
            return password_service.get_token_from_email(email)

    @task(1)
    def request_password_change(self):
        """Solicitar el formulario de cambio de contraseña."""
        email = "user1@example.com"  # Define el email del usuario
        reset_token = self.get_reset_token(email)
        if not reset_token:
            print("Failed to generate reset token")
            return

        # Solicita el formulario de cambio de contraseña
        response = self.client.get(f"/change/password/{reset_token}")
        if response.status_code != 200 or "Change password" not in response.text:
            print("Failed to load change password form")
            return

        csrf_token = get_csrf_token(response)
        if not csrf_token:
            print("Failed to retrieve CSRF token")
            return

        # Simular cambio de contraseña
        new_password = "NewPassword123!"  # Puedes usar una contraseña fija o generarla dinámicamente
        response = self.client.post(
            f"/change/password/{reset_token}",
            data={
                "password": new_password,
                "confirm_password": new_password,
                "csrf_token": csrf_token,
            },
        )

        if response.status_code == 302:
            print("Password changed successfully")
        else:
            print(f"Failed to change password: {response.status_code}")

    @task(1)
    def ensure_logged_out(self):
        """Cerrar sesión para asegurarse de que el estado esté limpio."""
        response = self.client.get("/logout")
        if response.status_code != 200:
            print(f"Logout failed or no active session: {response.status_code}")

    @task(1)
    def login(self):
        """Iniciar sesión con un usuario válido."""
        response = self.client.get("/login")
        if response.status_code != 200 or "Login" not in response.text:
            print("Already logged in or unexpected response, redirecting to logout")
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)
        if not csrf_token:
            print("Failed to retrieve CSRF token")
            return

        response = self.client.post(
            "/login",
            data={
                "email": "user1@example.com",
                "password": "1234",
                "csrf_token": csrf_token,
            },
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")


class AuthUser(HttpUser):
    """Usuario de prueba para Locust."""

    tasks = [ChangePasswordBehavior]
    min_wait = 1000  # 1 segundo
    max_wait = 3000  # 3 segundos
    host = "http://localhost:5000"  # Define la URL base de tu aplicación
