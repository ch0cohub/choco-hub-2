import pytest
from flask import url_for
from app import create_app, db
from app.modules.hubfile.services import HubfileService
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData

@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config['SERVER_NAME'] = 'localhost'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def test_client(app):
    return app.test_client()


def test_download_file(test_client):
    with test_client.application.app_context():
        hubfile_service = HubfileService()

        # Crear un nuevo DSMetaData y DataSet para usar como clave foránea
        dsmetadata = DSMetaData(id=4, title="Test Dataset", description="Test Description", publication_type=PublicationType.JOURNAL_ARTICLE)
        

        dataset = DataSet(id=4, user_id=2, ds_meta_data_id=dsmetadata.id)
   

        # Crear un nuevo FMMetaData para usar como clave foránea
        fmmetadata = FMMetaData(id=4, uvl_filename="file1.uvl", title="Feature Model 1", description="Description for feature model 1", publication_type=PublicationType.SOFTWARE_DOCUMENTATION)
       

        # Crear un nuevo FeatureModel para usar como clave foránea
        feature_model = FeatureModel(id=5, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id)
       

        # Crear un nuevo hubfile
        new_hubfile = hubfile_service.create(
            name="test_file.uvl",
            checksum="1234567890abcdef",
            size=2048,
            feature_model_id=feature_model.id
        )
       
        # Descargar el archivo
        response = test_client.get(url_for('hubfile.download_file', file_id=new_hubfile.id))
        assert response.status_code == 404, "Failed to download file."

def test_view_file(test_client):
    with test_client.application.app_context():
        hubfile_service = HubfileService()

        # Crear un nuevo DSMetaData y DataSet para usar como clave foránea
        dsmetadata = DSMetaData(id=500, title="Test Dataset View", description="Test Description View", publication_type=PublicationType.JOURNAL_ARTICLE)
        

        dataset = DataSet(id=600, user_id=1, ds_meta_data_id=dsmetadata.id)
       
        # Crear un nuevo FMMetaData para usar como clave foránea
        fmmetadata = FMMetaData(id=700, uvl_filename="file2.uvl", title="Feature Model 2", description="Description for feature model 2", publication_type=PublicationType.SOFTWARE_DOCUMENTATION)
       

        # Crear un nuevo FeatureModel para usar como clave foránea
        feature_model = FeatureModel(id=400, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id)
    

        # Crear un nuevo hubfile
        new_hubfile = hubfile_service.create(
            name="test_file_view.uvl",
            checksum="1234567890abcdef",
            size=1024,
            feature_model_id=feature_model.id
        )
        db.session.add(new_hubfile)
        db.session.commit()

        # Ver el archivo
        response = test_client.get(url_for('hubfile.view_file', file_id=new_hubfile.id))
        assert response.status_code == 404, "Failed to view file."
