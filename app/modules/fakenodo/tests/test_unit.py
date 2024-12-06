import pytest
from unittest.mock import MagicMock, patch
from app.modules.fakenodo.services import FakenodoService
from app.modules.fakenodo.models import Deposition
from app.modules.dataset.models import DataSet
from app import create_app
from app import db
from sqlalchemy import inspect

from app.modules.featuremodel.models import FeatureModel


@pytest.fixture
def fakenodo_service():
    return FakenodoService()


@pytest.fixture
def setup_deposition(app):
    with app.app_context():
        deposition = Deposition(id=1, dep_metadata={"title": "Test Deposition"}, status="draft", doi=None)
        db.session.add(deposition)
        db.session.commit()
        yield deposition
        db.session.delete(deposition)
        db.session.commit() 
        
              
@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", 
    })
    with app.app_context():
        inspector = inspect(db.engine)
        if "deposition" not in inspector.get_table_names():
            Deposition.__table__.create(db.engine)  
        yield app
        Deposition.__table__.drop(db.engine)


def test_create_new_deposition(fakenodo_service, app):
    with app.app_context():
        
        mock_dataset = MagicMock()    
        
        mock_dataset.ds_meta_data = MagicMock()
        mock_dataset.ds_meta_data.title = "Test Title"
        mock_dataset.ds_meta_data.description = "Test Description"      
        
        mock_dataset.ds_meta_data.publication_type = MagicMock()
        mock_dataset.ds_meta_data.publication_type.value = "none"      
        
        mock_author = MagicMock()
        mock_author.name = "Author1"
        mock_author.affiliation = "Test Affiliation"
        mock_author.orcid = "0000-0000"
        mock_dataset.ds_meta_data.authors = [mock_author]    
        
        mock_dataset.ds_meta_data.tags = "test, dataset"   
        
        mock_deposition = Deposition(id=1)  # Crear una instancia de Deposition con id
        with patch.object(fakenodo_service.deposition_repository, 'create_new_deposition',
                          return_value=mock_deposition) as mock_create:
            
            result = fakenodo_service.create_new_deposition(mock_dataset)          
            
            mock_create.assert_called_once()        
            
            assert result["id"] == 1
            assert result["message"] == "Deposition succesfully created in Fakenodo"
            

def test_upload_file(fakenodo_service, app):
    with app.app_context():
        mock_dataset = MagicMock(spec=DataSet)
        mock_feature_model = MagicMock(spec=FeatureModel)
        mock_feature_model.fm_meta_data.uvl_filename = "test_file.uvl"
        mock_user = MagicMock()
        mock_user.id = 1

        # Ya no es necesario el mock del checksum
        with patch("os.path.getsize", return_value=100):
            result = fakenodo_service.upload_file(mock_dataset, 1, mock_feature_model, user=mock_user)
            assert result["id"] == 1
            assert result["file"] == "test_file.uvl"
            assert result["fileSize"] == 100
            assert result["message"] == "File Uploaded to deposition with id 1"


def test_publish_deposition(fakenodo_service, app, setup_deposition):
    result = fakenodo_service.publish_deposition(setup_deposition.id)
    assert result["status"] == "published"
    assert result["conceptdoi"] == f"fakenodo.doi.{setup_deposition.id}"
    assert result["message"] == "Deposition published successfully in fakenodo."


def test_get_deposition(fakenodo_service, app, setup_deposition):
    result = fakenodo_service.get_deposition(setup_deposition.id)
    assert result["id"] == setup_deposition.id
    assert result["metadata"]["title"] == "Test Deposition"
    assert result["status"] == "draft"


def test_get_doi(fakenodo_service, app):
    with app.app_context():
        mock_deposition = MagicMock(spec=Deposition)
        mock_deposition.id = 1
        mock_deposition.doi = "fakenodo.doi.1"

        with patch.object(fakenodo_service, 'get_deposition', return_value={"doi": "fakenodo.doi.1"}):
            result = fakenodo_service.get_doi(1)
            assert result == "fakenodo.doi.1"
