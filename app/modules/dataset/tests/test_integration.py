import pytest
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.dataset.services import DataSetService
from flask_login import current_user
from app.modules.profile.models import UserProfile
from datetime import datetime

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


def test_dataset_list(test_client):
    """
    Test accessing the dataset list page.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/dataset/list")
    assert response.status_code == 200, "The dataset list page could not be accessed."
    assert b"Datasets" in response.data or b"No datasets" in response.data, "The expected content is not present on the page."

    logout(test_client)
    

def test_dataset_upload_bad_request(test_client):
    """
    Test uploading a new dataset.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.post(
        "/dataset/upload",
        data=dict(
            title="Test Dataset",
            description="This is a test dataset.",  
            dataset_file=(b"dataset content", "test_dataset.csv")
        ),
        content_type='multipart/form-data',
        follow_redirects=True
    )
    assert response.status_code == 400, "Dataset upload failed."
    logout(test_client)

def test_download_all_datasets(test_client):
    """Test downloading all datasets as a zip file."""
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    
    response = test_client.get("/dataset/download/all")
    
    # Comprobar que la respuesta sea exitosa (código 200)
    assert response.status_code == 200, "Download request failed."
    
    # Comprobar que la respuesta tiene el tipo de contenido adecuado para un archivo zip
    assert response.content_type == 'application/zip', f"Expected 'application/zip' but got {response.content_type}"
    
    # Verificar que el encabezado 'Content-Disposition' contiene 'attachment' y el nombre del archivo
    assert 'attachment' in response.headers['Content-Disposition'], "The response is not an attachment."
    assert 'zip' in response.headers['Content-Disposition'], "The file is not a zip file."
    
    # Verificar que el archivo descargado tenga un nombre apropiado
    today_date = datetime.now().strftime("%d_%m_%Y")
    expected_filename = f"chocohub2_datasets_from_{today_date}.zip"  
    assert expected_filename in response.headers['Content-Disposition'], f"Expected zip filename '{expected_filename}' but got {response.headers['Content-Disposition']}."
    
    logout(test_client)
    
    
def test_download_all_datasets_public_access(test_client):
    """Test downloading all datasets without authentication (public access)."""
    response = test_client.get("/dataset/download/all")
    
    # Verificar que la respuesta sea exitosa (código 200)
    assert response.status_code == 200, "Download request failed."
    
    # Verificar que el tipo de contenido sea 'application/zip'
    assert response.content_type == 'application/zip', f"Expected 'application/zip' but got {response.content_type}"
    
    # Verificar que el encabezado 'Content-Disposition' contenga 'attachment' y el nombre del archivo ZIP
    assert 'attachment' in response.headers['Content-Disposition'], "The response is not an attachment."
    assert 'zip' in response.headers['Content-Disposition'], "The file is not a zip file."
