import pytest
from unittest.mock import MagicMock, patch
from app.modules.fakenodo.services import FakenodoService
from app.modules.fakenodo.models import Deposition
from app import create_app
from app import db
from sqlalchemy import inspect


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
