import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile

import pytest
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app.modules.dataset.models import Dataset 

@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Se extiende test_client para añadir datos específicos para las pruebas de módulo.
    """
    with test_client.application.app_context():
        # Crear un usuario para pruebas
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname", is_verified=True)
        db.session.add(profile)
        db.session.commit()

        # Crear datasets para este usuario
        dataset_1 = Dataset(user_id=user_test.id, title="Test Dataset 1", publication_type="Research Paper")
        dataset_2 = Dataset(user_id=user_test.id, title="Test Dataset 2", publication_type="Article")
        db.session.add(dataset_1)
        db.session.add(dataset_2)
        db.session.commit()

    yield test_client

def test_user_datasets_page(test_client):
    """
    Se prueba el acceso a la página de datasets del usuario.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    
    # Acceder a la página de datasets del usuario
    response = test_client.get(f"/profile/{test_client.id}/datasets")
    assert response.status_code == 200, "The datasets page could not be accessed."
    
    # Comprobar si el contenido esperado está presente en la página
    assert b"User's Datasets" in response.data, "The page title is missing"
    assert b"Test Dataset 1" in response.data, "Dataset 1 is missing"
    assert b"Test Dataset 2" in response.data, "Dataset 2 is missing"
    assert b"Research Paper" in response.data, "Publication type is missing"

    logout(test_client)

def test_user_datasets_empty(test_client):
    """
    Prueba el acceso a la página de datasets de un usuario sin datasets.
    """
    # Crear un nuevo usuario sin datasets
    new_user = User(email='new_user@example.com', password='newpassword')
    db.session.add(new_user)
    db.session.commit()

    # Crear perfil para el nuevo usuario
    new_profile = UserProfile(user_id=new_user.id, name="New", surname="User", is_verified=True)
    db.session.add(new_profile)
    db.session.commit()

    # Login como el nuevo usuario
    login_response = login(test_client, "new_user@example.com", "newpassword")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Acceder a la página de datasets del nuevo usuario (sin datasets)
    response = test_client.get("/profile/datasets")
    assert response.status_code == 200, "The datasets page could not be accessed."
    
    # Comprobar si se muestra el mensaje de "No datasets found"
    assert b"No datasets found" in response.data, "No datasets message is missing"

    logout(test_client)

def test_access_without_login(test_client, user_test):
    """
    Prueba el acceso a la página de datasets de un usuario sin iniciar sesión.
    """
    response = test_client.get(f"/profile/{user_test.id}/datasets")
    assert response.status_code == 302, "The page should redirect to the login page."
    assert b"Login" in response.data, "The login page content is missing."

def test_user_datasets_pagination(test_client, user_test):
    """
    Prueba la paginación de los datasets de un usuario.
    """
    # Suponiendo que el usuario tiene más de un dataset
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    
    response = test_client.get(f"/profile/{user_test.id}/datasets?page=2")
    assert response.status_code == 200, "Pagination failed."
    assert b"Page 2" in response.data, "Pagination info is missing."
    logout(test_client)

def test_invalid_user_id(test_client):
    """
    Prueba el acceso a la página de datasets de un usuario con un ID de usuario no válido.
    """
    response = test_client.get("/profile/99999/datasets")
    assert response.status_code == 404, "Invalid user ID should return a 404 error."
    assert b"User not found" in response.data, "User not found message is missing."
