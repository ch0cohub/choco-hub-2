import pytest
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.dataset.services import DataSetService
from flask_login import current_user

@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
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
    
