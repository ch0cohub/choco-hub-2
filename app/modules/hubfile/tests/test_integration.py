import pytest
from flask import url_for
from app import create_app, db
from app.modules.auth.models import User
from app.modules.hubfile.services import HubfileService
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["SERVER_NAME"] = "localhost"
    app.config["APPLICATION_ROOT"] = "/"
    app.config["PREFERRED_URL_SCHEME"] = "http"
    with app.app_context(), app.test_request_context():
        yield app


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(id=2, email="user@example.com", password="test1234")
        UserProfile(name="Name", surname="Surname", is_verified=True, user=user_test)

        db.session.add(user_test)
        db.session.commit()

    yield test_client


@pytest.fixture(autouse=True)
def clean_db():
    """Rollback the database after each test."""
    db.session.begin_nested()
    yield
    db.session.rollback()
    db.session.remove()


def test_download_file(test_client):
    hubfile_service = HubfileService()

    # Configura los datos necesarios
    with test_client.application.app_context():
        dsmetadata = DSMetaData(
            id=200,
            title="Test Dataset",
            description="Test Description",
            publication_type=PublicationType.JOURNAL_ARTICLE,
        )
        db.session.add(dsmetadata)
        dataset = DataSet(id=300, user_id=2, ds_meta_data_id=dsmetadata.id)
        db.session.add(dataset)

        fmmetadata = FMMetaData(
            id=1000,
            uvl_filename="file1.uvl",
            title="Feature Model 1",
            description="Description for feature model 1",
            publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
        )
        db.session.add(fmmetadata)

        feature_model = FeatureModel(
            id=1100, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
        )
        db.session.add(feature_model)
        db.session.commit()

        # Crear el Hubfile dentro de la sesión activa
        new_hubfile = hubfile_service.create(
            name="test_file.uvl",
            checksum="1234567890abcdef",
            size=2048,
            feature_model_id=feature_model.id,
        )
        db.session.add(new_hubfile)
        db.session.commit()

        with test_client.application.test_request_context():
            download_url = url_for("hubfile.download_file", file_id=new_hubfile.id)

    # Realizar la solicitud fuera del contexto
    response = test_client.get(download_url)
    assert response.status_code == 404, "Failed to download file."


def test_view_file(test_client):
    hubfile_service = HubfileService()

    with test_client.application.app_context():
        dsmetadata = DSMetaData(
            id=500,
            title="Test Dataset View",
            description="Test Description View",
            publication_type=PublicationType.JOURNAL_ARTICLE,
        )
        db.session.add(dsmetadata)
        dataset = DataSet(id=600, user_id=2, ds_meta_data_id=dsmetadata.id)
        db.session.add(dataset)

        fmmetadata = FMMetaData(
            id=700,
            uvl_filename="file2.uvl",
            title="Feature Model 2",
            description="Description for feature model 2",
            publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
        )
        db.session.add(fmmetadata)

        feature_model = FeatureModel(
            id=400, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
        )
        db.session.add(feature_model)
        db.session.commit()

        new_hubfile = hubfile_service.create(
            name="test_file_view.uvl",
            checksum="1234567890abcdef",
            size=1024,
            feature_model_id=feature_model.id,
        )
        db.session.add(new_hubfile)
        db.session.commit()

        with test_client.application.test_request_context():
            view_url = url_for("hubfile.view_file", file_id=new_hubfile.id)

    # Realizar la solicitud fuera del contexto
    response = test_client.get(view_url)
    assert response.status_code == 404, "Failed to view file."
