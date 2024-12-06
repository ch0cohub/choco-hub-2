import pytest
from app.modules.explore.services import ExploreService
from app.modules.explore.repositories import ExploreRepository
from app.modules.dataset.seeders import DataSetSeeder
from app.modules.auth.seeders import AuthSeeder

# TEST OF EXPLORESERVICE
@pytest.fixture(scope="module")
def test_client(test_client):
    with test_client.application.app_context():
        user_seeder = AuthSeeder()
        user_seeder.run()
        dataset_seeder = DataSetSeeder()
        dataset_seeder.run()
    yield test_client

def test_filter_by_dataset_title_positive_service(test_client):
    search_criteria = {
        "title": "sample"
    }

    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)
    # 4 results
    assert len(result) == 4

def test_filter_by_dataset_title_negative_service():
    search_criteria = {
        "title": "abcd"
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)
    # 0 results
    assert len(result) == 0

def test_filter_by_dataset_tags_positive_service():
    search_criteria = {
        "tags_str": "tag1,tag2"
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)
    # 4 results
    assert len(result) == 4

def test_filter_by_dataset_tags_negative_service():
    search_criteria = {
        "tags_str": "tag3"
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)
    # 0 results
    assert len(result) == 0

# TEST OF EXPLOREREPOSITORY

def test_filter_by_dataset_title_positive_repository():
    search_criteria = {
        "title": "sample"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)
    # 4 results
    assert len(result) == 4

def test_filter_by_dataset_title_negative_repository():
    search_criteria = {
        "title": "abcd"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)
    # 0 results
    assert len(result) == 0

def test_filter_by_dataset_tags_positive_repository():
    search_criteria = {
        "tags_str": "tag1,tag2"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)
    # 4 results
    assert len(result) == 4

def test_filter_by_dataset_tags_negative_repository():
    search_criteria = {
        "tags_str": "tag3"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)
    # 0 results
    assert len(result) == 0
