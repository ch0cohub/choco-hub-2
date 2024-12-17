from app.modules.dataset.models import (
    DSMetaData,
    DataSet,
    DatasetReview,
    PublicationType,
)
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
        user_test = User(email="user@example.com", password="test1234")
        UserProfile(name="Name", surname="Surname", is_verified=True, user=user_test)
        db.session.add(user_test)
        db.session.commit()

        dsmetadata = DSMetaData(
            id=1,
            title="Test Dataset",
            description="Test Description",
            publication_type=PublicationType.JOURNAL_ARTICLE,
            dataset_doi="10.1234/testdataset",
            tags="tag1,tag2",  # Make sure tags are provided, even if just as a test
        )
        db.session.add(dsmetadata)

        dataset = DataSet(id=1, user_id=1, ds_meta_data_id=dsmetadata.id)
        db.session.add(dataset)

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
    assert (
        b"Datasets" in response.data or b"No datasets" in response.data
    ), "The expected content is not present on the page."

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
            dataset_file=(b"dataset content", "test_dataset.csv"),
        ),
        content_type="multipart/form-data",
        follow_redirects=True,
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
    assert (
        response.content_type == "application/zip"
    ), f"Expected 'application/zip' but got {response.content_type}"

    # Verificar que el encabezado 'Content-Disposition' contiene 'attachment' y el nombre del archivo
    assert (
        "attachment" in response.headers["Content-Disposition"]
    ), "The response is not an attachment."
    assert (
        "zip" in response.headers["Content-Disposition"]
    ), "The file is not a zip file."

    # Verificar que el archivo descargado tenga un nombre apropiado
    today_date = datetime.now().strftime("%d_%m_%Y")
    expected_filename = f"chocohub2_datasets_from_{today_date}.zip"
    assert (
        expected_filename in response.headers["Content-Disposition"]
    ), f"Expected zip filename '{expected_filename}' but got {response.headers['Content-Disposition']}."

    logout(test_client)


def test_download_all_datasets_public_access(test_client):
    """Test downloading all datasets without authentication (public access)."""
    response = test_client.get("/dataset/download/all")

    # Verificar que la respuesta sea exitosa (código 200)
    assert response.status_code == 200, "Download request failed."

    # Verificar que el tipo de contenido sea 'application/zip'
    assert (
        response.content_type == "application/zip"
    ), f"Expected 'application/zip' but got {response.content_type}"

    # Verificar que el encabezado 'Content-Disposition' contenga 'attachment' y el nombre del archivo ZIP
    assert (
        "attachment" in response.headers["Content-Disposition"]
    ), "The response is not an attachment."
    assert (
        "zip" in response.headers["Content-Disposition"]
    ), "The file is not a zip file."


def test_like_dataset_new_review(test_client):
    """
    Test adding a new like (value=1) for a dataset.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Send POST request to like the dataset
    response = test_client.post(
        "/api/dataset/like",
        json={"dataset_id": 1, "value": 1},
        follow_redirects=True,
    )
    assert response.status_code == 200, "Like request failed."
    data = response.get_json()
    assert data["total_likes"] == "1", "Total likes count is incorrect."

    # Verify the review is created in the database
    with test_client.application.app_context():
        review = DatasetReview.query.filter_by(
            data_set_id=1, user_id=current_user.id
        ).first()
        assert review is not None, "Review was not created."
        assert review.value == 1, "Review value is incorrect."

    logout(test_client)


def test_like_dataset_update_review(test_client):
    """
    Test updating an existing review (change value to -1).
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Send POST request to update the review
    response = test_client.post(
        "/api/dataset/like",
        json={"dataset_id": 1, "value": -1},
        follow_redirects=True,
    )
    assert response.status_code == 200, "Update like request failed."
    data = response.get_json()
    assert data["total_likes"] == "-1", "Total likes count is incorrect after update."

    # Verify the review is updated in the database
    with test_client.application.app_context():
        review = DatasetReview.query.filter_by(
            data_set_id=1, user_id=current_user.id
        ).first()
        assert review is not None, "Review does not exist."
        assert review.value == -1, "Review value was not updated correctly."

    logout(test_client)


def test_like_dataset_invalid_input(test_client):
    """
    Test the endpoint with invalid input (missing dataset_id or invalid value).
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Test missing dataset_id
    response = test_client.post(
        "/api/dataset/like",
        json={"value": 1},
        follow_redirects=True,
    )
    assert response.status_code == 400, "Invalid input did not return 400 status code."
    data = response.get_json()
    assert "error" in data, "Error message not returned for missing dataset_id."

    # Test invalid value
    response = test_client.post(
        "/api/dataset/like",
        json={"dataset_id": 1, "value": 5},
        follow_redirects=True,
    )
    assert response.status_code == 400, "Invalid value did not return 400 status code."
    data = response.get_json()
    assert "error" in data, "Error message not returned for invalid value."

    logout(test_client)
