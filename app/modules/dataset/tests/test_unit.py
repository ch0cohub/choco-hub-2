from unittest.mock import MagicMock
import pytest
from app import create_app
from app.modules.dataset.models import DSMetaData, DataSet, PublicationType
from app.modules.dataset.services import DataSetService
from pathlib import Path
import zipfile
from datetime import datetime
from app import db
from app.modules.featuremodel.models import FMMetaData, FeatureModel


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        dsmetadata = DSMetaData(id=1, title="Test Dataset", description="Test Description", publication_type=PublicationType.JOURNAL_ARTICLE, dataset_doi="10.1234/testdataset")
        db.session.add(dsmetadata)

        dataset = DataSet(id=1, user_id=1, ds_meta_data_id=dsmetadata.id)
        db.session.add(dataset)
        
        db.session.commit()
    yield test_client  

      
@pytest.fixture(scope="module")
def dataset_service(test_client):
    service = DataSetService()
    return service

 
def test_should_insert_author(dataset_service):
    initial_authors_count = dataset_service.count_authors()
    new_author = { 
        "name": "author",
        "affiliation": "affiliation",
        "orcid": "0000-0001-0002-0003"
    }
    test_author = dataset_service.author_repository.create(**new_author)
    dataset_service.repository.session.commit()
    
    assert test_author is not None
    assert test_author.name == new_author["name"]
    assert test_author.affiliation == new_author["affiliation"]
    assert test_author.orcid == new_author["orcid"]
    assert initial_authors_count + 1 == dataset_service.count_authors()
    
    
def test_get_synchronized(dataset_service):
    user_id = 3 
    dataset = dataset_service.get_synchronized(user_id)
    assert dataset is not None
    
    
def test_get_unsynchronized(dataset_service):
    user_id = 1
    dataset = dataset_service.get_unsynchronized(user_id)
    assert dataset is not None
    
    
def test_total_dataset_downloads(dataset_service):
    total_downloads = dataset_service.total_dataset_downloads()
    assert isinstance(total_downloads, int)
    
    
def test_get_synchronized_datasets(dataset_service):
    datasets = dataset_service.get_synchronized_datasets()
    assert datasets is not None
    
    
def test_generate_datasets_and_name_zip(dataset_service, test_client):
    temp_dataset_path = Path("/tmp/Test_Dataset")
    temp_dataset_path.mkdir(parents=True, exist_ok=True)

    temp_file = temp_dataset_path / "file7.uvl"
    temp_file.write_text("Contenido del archivo UVL de prueba")

    dataset_service.get_synchronized_datasets = MagicMock(return_value=[
        ("Test Dataset", str(temp_dataset_path))
    ])

    zip_path, zip_filename = dataset_service.generate_datasets_and_name_zip()

    with zipfile.ZipFile(zip_path, "r") as zipf:
        zip_content = zipf.namelist()

    today_date = datetime.now().strftime("%d_%m_%Y")
    expected_filename = f"chocohub2_datasets_from_{today_date}.zip"
    assert zip_filename == expected_filename, (
        f"El nombre del archivo es incorrecto. "
        f"Esperado: {expected_filename}, Encontrado: {zip_filename}"
    )

    assert Path(zip_path).exists()
    assert zip_filename.endswith(".zip")
    assert len(zip_content) == 1  
    assert zip_content[0] == "Test Dataset/file7.uvl"  

    Path(zip_path).unlink()
    temp_file.unlink()
    temp_dataset_path.rmdir()