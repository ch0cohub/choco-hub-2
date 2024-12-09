import pytest
from app.modules.dataset.models import DSDownloadRecord, DSViewRecord
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

def test_sort_by_most_downloaded_positive_service():
    search_criteria = {
        "sorting": "most downloads"
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)

    datasets_with_downloads = []
    for dataset in result:
        download_count = DSDownloadRecord.query.filter_by(dataset_id=dataset.id).count()
        datasets_with_downloads.append((dataset, download_count))

    # Verificar que la lista está ordenada de más a menos por descargas
    assert all(
        datasets_with_downloads[i][1] >= datasets_with_downloads[i + 1][1]
        for i in range(len(datasets_with_downloads) - 1)
    )

def test_sort_by_most_views_positive_service():
    search_criteria = {
        "sorting": "most views"
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)

    datasets_with_views = []
    for dataset in result:
        view_count = DSViewRecord.query.filter_by(dataset_id=dataset.id).count()
        datasets_with_views.append((dataset, view_count))

    # Verificar que la lista está ordenada de más a menos por vistas
    assert all(
        datasets_with_views[i][1] >= datasets_with_views[i + 1][1]
        for i in range(len(datasets_with_views) - 1)
    ), "El orden por vistas no es correcto."

def test_filter_by_uvl_validation_positive_service():
    search_criteria = {
        "uvl_validation": True
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)

    # Verificar que todos los datasets tienen modelos de características con uvl_valid == True
    assert all(
        all(feature_model.uvl_valid is True for feature_model in dataset.feature_models)
        for dataset in result
    ), "Algunos datasets tienen modelos de características no validados correctamente (uvl_valid == False)."

    assert len(result) == 0

def test_filter_by_uvl_validation_negative_service():
    search_criteria = {
        "uvl_validation": False  # El filtro no debería excluir datasets con modelos no validados
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)

    # Verificar que los datasets pueden contener modelos de características con uvl_valid == False
    assert any(
        feature_model.uvl_valid is False for dataset in result for feature_model in dataset.feature_models
    ), "El filtro debería permitir datasets con modelos de características no validados (uvl_valid == False)."

    assert len(result) == 4

def test_filter_by_num_authors_1():
    # Filtro con num_authors igual a "1"
    search_criteria = {
        "num_authors": "1"
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)

    # Verificar que el número de datasets que lo cumplen es 4
    assert len(result) == 4

def test_filter_by_num_authors_2_3():
    # Filtro con num_authors igual a "2-3"
    search_criteria = {
        "num_authors": "2-3"
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)

    # Verificar que ningún dataset cumple con el filtro
    assert len(result) == 0

def test_filter_by_num_authors_4_plus():
    search_criteria = {
        "num_authors": "4+"
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)

    #Verificar que ningún dataset cumple con el filtro
    assert len(result) == 0

def test_combined_filter_sort_validation_and_num_authors():
    search_criteria = {
        "sorting": "most downloads",
        "uvl_validation": True,
        "num_authors": "1"
    }
    explore_service = ExploreService()
    result = explore_service.filter(search_criteria)

    # Verificar que los datasets cumplen con el filtro de validación UVL
    assert all(
        all(feature_model.uvl_valid is True for feature_model in dataset.feature_models)
        for dataset in result
    ), "Algunos datasets tienen modelos de características no validados correctamente (uvl_valid == False)."

    # Verificar que todos los datasets tienen exactamente 1 autor
    for dataset in result:
        author_count = len(dataset.ds_meta_data.authors)
        assert author_count == 1, f"Dataset {dataset.id} no tiene exactamente 1 autor."

    # Verificar el orden por descargas
    datasets_with_downloads = []
    for dataset in result:
        download_count = DSDownloadRecord.query.filter_by(dataset_id=dataset.id).count()
        datasets_with_downloads.append((dataset, download_count))

    assert all(
        datasets_with_downloads[i][1] >= datasets_with_downloads[i + 1][1]
        for i in range(len(datasets_with_downloads) - 1)
    ), "El orden por descargas no es correcto."

    #Este debe ser el resultado por como funciona la validación de los archivos UVL
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

def test_sort_by_most_downloaded_repository():
    search_criteria = {
        "sorting": "most downloads"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)

    datasets_with_downloads = []
    for dataset in result:
        download_count = DSDownloadRecord.query.filter_by(dataset_id=dataset.id).count()
        datasets_with_downloads.append((dataset, download_count))

    assert all(
        datasets_with_downloads[i][1] >= datasets_with_downloads[i + 1][1]
        for i in range(len(datasets_with_downloads) - 1)
    )


def test_sort_by_most_views_repository():
    search_criteria = {
        "sorting": "most views"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)

    datasets_with_views = []
    for dataset in result:
        view_count = DSViewRecord.query.filter_by(dataset_id=dataset.id).count()
        datasets_with_views.append((dataset, view_count))

    assert all(
        datasets_with_views[i][1] >= datasets_with_views[i + 1][1]
        for i in range(len(datasets_with_views) - 1)
    ), "El orden por vistas no es correcto."


def test_filter_by_uvl_validation_positive_repository():
    search_criteria = {
        "uvl_validation": True
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)

    assert all(
        all(feature_model.uvl_valid is True for feature_model in dataset.feature_models)
        for dataset in result
    ), "Algunos datasets tienen modelos de características no validados correctamente (uvl_valid == False)."

    assert len(result) == 0


def test_filter_by_uvl_validation_negative_repository():
    search_criteria = {
        "uvl_validation": False
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)

    assert any(
        feature_model.uvl_valid is False for dataset in result for feature_model in dataset.feature_models
    ), "El filtro debería permitir datasets con modelos de características no validados (uvl_valid == False)."

    assert len(result) == 4

def test_filter_by_num_authors_1_repository():
    search_criteria = {
        "num_authors": "1"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)

    assert len(result) == 4


def test_filter_by_num_authors_2_3_repository():
    search_criteria = {
        "num_authors": "2-3"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)

    assert len(result) == 0


def test_filter_by_num_authors_4_plus_repository():
    search_criteria = {
        "num_authors": "4+"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)

    assert len(result) == 0


def test_combined_filter_sort_validation_and_num_authors_repository():
    search_criteria = {
        "sorting": "most downloads",
        "uvl_validation": True,
        "num_authors": "1"
    }
    explore_repository = ExploreRepository()
    result = explore_repository.filter(search_criteria)

    # Verificar que los datasets cumplen con el filtro de validación UVL
    assert all(
        all(feature_model.uvl_valid is True for feature_model in dataset.feature_models)
        for dataset in result
    ), "Algunos datasets tienen modelos de características no validados correctamente (uvl_valid == False)."

    # Verificar que todos los datasets tienen exactamente 1 autor
    for dataset in result:
        author_count = len(dataset.ds_meta_data.authors)
        assert author_count == 1, f"Dataset {dataset.id} no tiene exactamente 1 autor."

    # Verificar el orden por descargas
    datasets_with_downloads = []
    for dataset in result:
        download_count = DSDownloadRecord.query.filter_by(dataset_id=dataset.id).count()
        datasets_with_downloads.append((dataset, download_count))

    assert all(
        datasets_with_downloads[i][1] >= datasets_with_downloads[i + 1][1]
        for i in range(len(datasets_with_downloads) - 1)
    ), "El orden por descargas no es correcto."

    #Este debe ser el resultado por como funciona la validación de los archivos UVL
    assert len(result) == 0