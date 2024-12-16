# FILE: app/modules/hubfile/tests/test_unit.py

import pytest
from flask import url_for
from app import create_app, db
from app.modules.hubfile.models import Hubfile
from app.modules.hubfile.services import HubfileService
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["SERVER_NAME"] = "localhost"
    app.config["APPLICATION_ROOT"] = "/"
    app.config["PREFERRED_URL_SCHEME"] = "http"
    with app.app_context():
        yield app


def test_total_downloads(test_client):
    with test_client.application.app_context():
        download_service = HubfileService()
        total_downloads = download_service.total_hubfile_downloads()
        assert total_downloads >= 0, "Total downloads count is incorrect."


def test_total_views(test_client):
    with test_client.application.app_context():
        hubfile_service = HubfileService()
        total_views = hubfile_service.total_hubfile_views()
        assert total_views >= 0, "Total views count is incorrect."


def test_create_hubfile(test_client):
    with test_client.application.app_context():
        hubfile_service = HubfileService()

        # New DSMetaData y DataSet for testing
        dsmetadata = DSMetaData(
            id=1,
            title="Test Dataset",
            description="Test Description",
            publication_type=PublicationType.JOURNAL_ARTICLE,
        )
        db.session.add(dsmetadata)
        db.session.commit()

        dataset = DataSet(id=1, user_id=1, ds_meta_data_id=dsmetadata.id)
        db.session.add(dataset)
        db.session.commit()
        # New FMMetaData for testing
        fmmetadata = FMMetaData(
            id=1,
            uvl_filename="file1.uvl",
            title="Feature Model 1",
            description="Description for feature model 1",
            publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
        )
        db.session.add(fmmetadata)
        db.session.commit()
        # Create a new DSMetaData and DataSet to use as a foreign key before creating a new FeatureModel
        feature_model = FeatureModel(
            id=99, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
        )
        db.session.add(feature_model)
        db.session.commit()
        # Create a new hubfile
        new_hubfile = hubfile_service.create(
            name="test_file.uvl",
            checksum="1234567890abcdef",
            size=1024,
            feature_model_id=feature_model.id,
        )
        assert new_hubfile is not None, "Failed to create new hubfile."
        assert new_hubfile.name == "test_file.uvl", "Hubfile name mismatch."
        assert new_hubfile.checksum == "1234567890abcdef", "Hubfile checksum mismatch."
        assert new_hubfile.size == 1024, "Hubfile size mismatch."


def test_delete_hubfile(test_client):
    with test_client.application.app_context():
        hubfile_service = HubfileService()

        # New DSMetaData y DataSet for testing
        dsmetadata = DSMetaData(
            id=2,
            title="Test Dataset",
            description="Test Description",
            publication_type=PublicationType.JOURNAL_ARTICLE,
        )
        db.session.add(dsmetadata)
        db.session.commit()

        dataset = DataSet(id=2, user_id=1, ds_meta_data_id=dsmetadata.id)
        db.session.add(dataset)
        db.session.commit()
        # New FMMetaData for testing
        fmmetadata = FMMetaData(
            id=2,
            uvl_filename="file1.uvl",
            title="Feature Model 1",
            description="Description for feature model 1",
            publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
        )
        db.session.add(fmmetadata)
        db.session.commit()
        # Create a new DSMetaData and DataSet to use as a foreign key before creating a new FeatureModel
        feature_model = FeatureModel(
            id=100, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
        )
        db.session.add(feature_model)
        db.session.commit()
        # Create a new hubfile
        new_hubfile = hubfile_service.create(
            name="test_file.uvl",
            checksum="1234567890abcdef",
            size=1024,
            feature_model_id=feature_model.id,
        )

        # Eliminar el hubfile
        hubfile_service.delete(new_hubfile.id)
        deleted_hubfile = hubfile_service.get_by_id(new_hubfile.id)
        assert deleted_hubfile is None, "Failed to delete hubfile."
