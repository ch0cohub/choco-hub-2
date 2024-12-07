import pytest
from flask import url_for
from app import create_app, db
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app.modules.auth.services import AuthenticationService
from app.modules.signupvalidation.services import SignupvalidationService
from app.modules.auth.services import AuthenticationService
from app.modules.conftest import login
from app import mail_configuration


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        UserProfile(name="Name", surname="Surname", is_verified=True, user=user_test)

        db.session.add(user_test)
        db.session.commit()

    yield test_client
            
            


def test_user_signup_and_confirmation(test_client):
    signup_service = SignupvalidationService()
    
    # Datos de prueba para el registro
    user_data = {
        'email': 'newuser@example.com',
        'password': 'newpassword123',
        'confirm_password': 'newpassword123',
        'name': 'New',
        'surname': 'User'
    }
    
    # 1. Registro de usuario
    response = test_client.post('/signup/', data=user_data, follow_redirects=True)
    
    # Asegurarse de que la respuesta es exitosa
    assert response.status_code == 200, "Registration failed."
    
    with test_client.application.app_context():
        # Verificar si el usuario fue creado en la base de datos
        user = User.query.filter_by(email=user_data['email']).first()
        assert user is not None, "New user was not created in the database."
        
        
        # Generar el token de confirmación para este usuario
        token = signup_service.get_token_from_email(user_data['email'])
        assert token is not None, "Token generation failed"
        
        # Obtener el enlace de confirmación

        
        signup_service.confirm_user_with_token(token=token)
        
        # 3. Verificar que el usuario ha sido confirmado
        user = User.query.filter_by(email=user_data['email']).first()
        assert user.profile.is_verified is True, "The user was not confirmed correctly."
        




def test_signup_duplicate_email(test_client):
    """
    Test para verificar que el sistema no permita registros con el mismo correo electrónico.
    """
    # Crear el primer usuario
    form_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "name": "Test",
        "surname": "User"
    }
    test_client.post('/signup/', data=form_data)

    # Intentar registrar un segundo usuario con el mismo correo
    response = test_client.post('/signup/', data=form_data)

    # Verificar que la respuesta contiene el error de email duplicado
    assert b"Email duplicate@example.com in use" in response.data


def test_signup_invalid_email(test_client):
    """
    Test para verificar que el sistema maneje correctamente un correo electrónico no válido.
    """
    # Datos con un email no válido
    form_data = {
        "email": "invalid-email",
        "password": "password123",
        "name": "Test",
        "surname": "User"
    }

    # Hacer la petición para registrar al usuario
    response = test_client.post('/signup/', data=form_data)

    # Verificar que la respuesta contiene el error adecuado
    assert b"Invalid email address" in response.data
