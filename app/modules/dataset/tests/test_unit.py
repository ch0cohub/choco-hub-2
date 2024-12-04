import pytest
from app import create_app
from app.modules.dataset.services import DataSetService
from pathlib import Path
import zipfile
from datetime import datetime

@pytest.fixture(scope="module")
def app():
    app = create_app()
    with app.app_context():
        yield app
        
        
@pytest.fixture(scope="module")
def dataset_service(app):
    service = DataSetService()
    return service


@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        pass
    yield test_client
    
    
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
    assert len(datasets) == 4
    
    
def test_generate_datasets_and_name_zip(dataset_service):
    
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
    assert len(zip_content) == 12
    Path(zip_path).unlink()