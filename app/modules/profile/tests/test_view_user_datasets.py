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
from app.modules.dataset.models import DataSet, PublicationType, DSMetaData

@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Se extiende test_client para añadir datos específicos para las pruebas de módulo.
    """
    with test_client.application.app_context():
        # Crear un usuario para pruebas
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()  # Commit first to assign user_test.id

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname", is_verified=True)
        db.session.add(profile)
        db.session.commit()


        # Crear datasets para este usuario  
        dsmetadate1 = DSMetaData(id=200, title="Test Dataset 1", description="description", publication_type=PublicationType.JOURNAL_ARTICLE)
        db.session.add(dsmetadate1)
        dsmetadate2 = DSMetaData(id=201, title="Test Dataset 2", description="description", publication_type=PublicationType.JOURNAL_ARTICLE)
        db.session.add(dsmetadate2)
        dsmetadate3 = DSMetaData(id=202, title="Test Dataset 6", description="description", publication_type=PublicationType.JOURNAL_ARTICLE)
        db.session.add(dsmetadate3)
        dataset_1 = DataSet(id=300, user_id=1, ds_meta_data_id = 200)
        dataset_2 = DataSet(id=301, user_id=1, ds_meta_data_id = 201)
        dataset_3 = DataSet(id=302, user_id=1, ds_meta_data_id = 201)
        dataset_4 = DataSet(id=303, user_id=1, ds_meta_data_id = 201)
        dataset_5 = DataSet(id=304, user_id=1, ds_meta_data_id = 201)
        dataset_6 = DataSet(id=305, user_id=1, ds_meta_data_id = 202)
        dataset_7 = DataSet(id=306, user_id=2, ds_meta_data_id = 200)
        db.session.add(dataset_1)
        db.session.add(dataset_2)
        db.session.add(dataset_3)
        db.session.add(dataset_4)
        db.session.add(dataset_5)
        db.session.add(dataset_6)
        db.session.add(dataset_7)
        db.session.commit()

    yield test_client

def test_one_user_dataset_page(test_client):
    """
    Se prueba el acceso a la página de datasets del usuario con uno solo.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    
    response = test_client.get("/profile/2/datasets")
    assert response.status_code == 200, "The datasets page could not be accessed."
    
    # Comprobar si el contenido esperado está presente en la página
    assert b"User's Datasets" in response.data, "The page title is missing"
    assert b"Test Dataset 1" in response.data, "Dataset 1 is missing"
    assert b"Journal Article" in response.data, "Publication type is missing"

    logout(test_client)

def test_user_datasets_page(test_client):
    """
    Se prueba el acceso a la página de datasets del usuario con varios.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    
    response = test_client.get("/profile/1/datasets")
    assert response.status_code == 200, "The datasets page could not be accessed."
    
    # Comprobar si el contenido esperado está presente en la página
    assert b"User's Datasets" in response.data, "The page title is missing"
    assert b"Test Dataset 1" in response.data, "Dataset 1 is missing"
    assert b"Test Dataset 2" in response.data, "Dataset 2 is missing"
    assert b"Journal Article" in response.data, "Publication type is missing"

    logout(test_client)


def test_user_datasets_empty(test_client):
    """
    Prueba el acceso a la página de datasets de un usuario sin datasets.
    SE ENCUENTRA ERROR: la ruta usaba la id de UserProfile, y no la de User, lo cual suele ser igual pero no necesariamente es así siempre, como se daba en el problema que se generaba, se procede a corregir
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

    # Access the datasets page using the new user's ID dynamically
    response = test_client.get(f"/profile/{new_user.id}/datasets")
    assert response.status_code == 200, "The datasets page could not be accessed."
    
    # Comprobar si se muestra el mensaje de "No datasets found"
    assert b"No datasets found" in response.data, "No datasets message is missing"

    logout(test_client)


def test_access_without_login(test_client):
    """
    Prueba el acceso a la página de datasets de un usuario sin iniciar sesión.
    """
    response = test_client.get(f"/profile/1/datasets")
    assert response.status_code == 302, "The page should redirect to the login page."


def test_user_datasets_pagination(test_client):
    """
    Prueba la paginación de los datasets de un usuario.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get(f"/profile/1/datasets?page=2")
    assert response.status_code == 200, "Pagination failed."
    assert b"Test Dataset 6" in response.data, "Pagination info is missing."

    logout(test_client)


def test_invalid_user_id(test_client):
    """
    Prueba el acceso a la página de datasets de un usuario con un ID de usuario no válido.
    SE ENCUENTRA ERROR: NO ESTABA CONTEMPLADA LA SITUACIÓN QUE EL USUARIO NO EXISTA, SE PROCEDE A CORREGIR
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    response = test_client.get("/profile/99999/datasets")
    assert response.status_code == 404, "Invalid user ID should return a 404 error."
    logout(test_client)
