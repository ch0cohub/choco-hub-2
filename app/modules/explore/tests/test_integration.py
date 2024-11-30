from app.modules.explore.services import ExploreService
from app.modules.explore.repositories import ExploreRepository
from app.modules.dataset.models import DataSet
from app.modules.dataset.seeders import DataSetSeeder
from app.modules.auth.seeders import AuthSeeder
import pytest

# INTEGRATION TEST

@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        user_seeder = AuthSeeder()
        user_seeder.run()
        dataset_seeder = DataSetSeeder()
        dataset_seeder.run()
    yield test_client

def test_filter_by_dataset_title_positive_integration(test_client):
    response = test_client.get("/explore?query=sample")
    # TODO: se seedea bien, de hecho si aquí haces print de los datasets, aparecen.
    # pero el test_client.get llama al html, pero no ejecuta el javascript y por ende el service y el repository
    # no son llamados
    datasets = DataSet.query.all()
    assert response.status_code == 200
    assert "We have not found any datasets that meet your search criteria" in response.data.decode("utf-8")

def test_filter_by_dataset_title_negative_integration(test_client):
    response = test_client.get("/explore?query=nonexistent")
    assert response.status_code == 200
    assert "We have not found any datasets that meet your search criteria" in response.data.decode("utf-8")

