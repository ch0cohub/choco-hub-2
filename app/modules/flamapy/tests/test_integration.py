import pytest
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.dataset.models import DSMetaData, DataSet, PublicationType
from app.modules.dataset.services import DataSetService
from flask_login import current_user
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from app.modules.hubfile.models import Hubfile
from app.modules.profile.models import UserProfile
from datetime import datetime

@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        UserProfile(name="Name", surname="Surname", is_verified=True, user=user_test)
        db.session.add(user_test)
        db.session.commit()

    yield test_client



# @pytest.fixture
# def test_dataset():
#     """
#     Fixture que crea un dataset de prueba con datos relacionados.
#     """
#     # Crear usuario
    
#     user_test = User(id= 1000, email='user@example33.com', password='test1234')
#     UserProfile(name="Name", surname="Surname", is_verified=True, user=user_test)
#     db.session.add(user_test)
#     # Crear DSMetaData
#     ds_metadata = DSMetaData(
#         title="Test Dataset Title",
#         description="A description for the test dataset",
#         publication_type=PublicationType.JOURNAL_ARTICLE,
#         tags="test, dataset"
#     )
#     db.session.add(ds_metadata)

#     # Crear DataSet
#     dataset = DataSet(
#         user_id=user_test.id,
#         ds_meta_data=ds_metadata
#     )
#     db.session.add(dataset)

#     # Crear FMMetaData
    

#     db.session.commit()  # Confirmar todos los cambios en la base de datos.

#     yield dataset  # Devuelve el dataset para usarlo en las pruebas.

#     # Limpieza de la base de datos
#     db.session.delete(dataset)
#     db.session.delete(ds_metadata)
#     db.session.commit()


def test_download_glencoe_dataset(test_client):
    """
    Prueba la descarga de un dataset en formato Glencoe.
    """
    
    
    user_test = User(id= 1000, email='user@example33.com', password='test1234')
    UserProfile(name="Name", surname="Surname", is_verified=True, user=user_test)
    db.session.add(user_test)
    # Crear DSMetaData
    ds_metadata = DSMetaData(
        title="Test Dataset Title",
        description="A description for the test dataset",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        tags="test, dataset"
    )
    db.session.add(ds_metadata)

    # Crear DataSet
    dataset = DataSet(
        user_id=user_test.id,
        ds_meta_data=ds_metadata
    )
    db.session.add(dataset)
 

    db.session.commit()  # Confirmar todos los cambios en la base de datos.
  # Devuelve el dataset para usarlo en las pruebas.

    # Limpieza de la base de datos
    
    
    
    # URL de la ruta que queremos probar
    dataset_id = dataset.id
    url = f"/flamapy/download/GLENCOE/{dataset_id}"

    # Realizar la solicitud GET
    response = test_client.get(url)

    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Verificar que el contenido sea un archivo ZIP
    assert "application/zip" in response.content_type, "The response is not a ZIP file."

    # Verificar que el nombre del archivo ZIP sea el esperado
    expected_filename = f"{dataset.ds_meta_data.title}_glencoe.zip"
    content_disposition = response.headers.get("Content-Disposition", "")
    assert expected_filename in content_disposition, f"Expected filename '{expected_filename}', got '{content_disposition}'"
    db.session.delete(dataset)
    db.session.delete(ds_metadata)
    db.session.commit()
    



def test_download_dimacs_dataset(test_client):
    """
    Prueba la descarga de un dataset en formato Glencoe.
    """
    
    
    user_test = User(id= 1001, email='user@example333.com', password='test1234')
    UserProfile(name="Name", surname="Surname", is_verified=True, user=user_test)
    db.session.add(user_test)
    # Crear DSMetaData
    ds_metadata = DSMetaData(
        title="Test Dataset Title",
        description="A description for the test dataset",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        tags="test, dataset"
    )
    db.session.add(ds_metadata)

    # Crear DataSet
    dataset = DataSet(
        user_id=user_test.id,
        ds_meta_data=ds_metadata
    )
    db.session.add(dataset)
 

    db.session.commit()  # Confirmar todos los cambios en la base de datos.
    
    # URL de la ruta que queremos probar
    dataset_id = dataset.id
    url = f"/flamapy/download/DIMACS/{dataset_id}"

    # Realizar la solicitud GET
    response = test_client.get(url)

    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Verificar que el contenido sea un archivo ZIP
    assert "application/zip" in response.content_type, "The response is not a ZIP file."

    # Verificar que el nombre del archivo ZIP sea el esperado
    expected_filename = f"{dataset.ds_meta_data.title}_dimacs.zip"
    content_disposition = response.headers.get("Content-Disposition", "")
    assert expected_filename in content_disposition, f"Expected filename '{expected_filename}', got '{content_disposition}'"
    db.session.delete(dataset)
    db.session.delete(ds_metadata)
    db.session.commit()
    


def test_download_SPLOT_dataset(test_client):
    """
    Prueba la descarga de un dataset en formato Glencoe.
    """
    
    
    user_test = User(id= 1002, email='user@example3333.com', password='test1234')
    UserProfile(name="Name", surname="Surname", is_verified=True, user=user_test)
    db.session.add(user_test)
    # Crear DSMetaData
    ds_metadata = DSMetaData(
        title="Test Dataset Title",
        description="A description for the test dataset",
        publication_type=PublicationType.JOURNAL_ARTICLE,
        tags="test, dataset"
    )
    db.session.add(ds_metadata)

    # Crear DataSet
    dataset = DataSet(
        user_id=user_test.id,
        ds_meta_data=ds_metadata
    )
    db.session.add(dataset)
 

    db.session.commit()  # Confirmar todos los cambios en la base de datos.
    
    # URL de la ruta que queremos probar
    dataset_id = dataset.id
    url = f"/flamapy/download/SPLOT/{dataset_id}"

    # Realizar la solicitud GET
    response = test_client.get(url)

    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Verificar que el contenido sea un archivo ZIP
    assert "application/zip" in response.content_type, "The response is not a ZIP file."

    # Verificar que el nombre del archivo ZIP sea el esperado
    expected_filename = f"{dataset.ds_meta_data.title}_splot.zip"
    content_disposition = response.headers.get("Content-Disposition", "")
    assert expected_filename in content_disposition, f"Expected filename '{expected_filename}', got '{content_disposition}'"
    db.session.delete(dataset)
    db.session.delete(ds_metadata)
    db.session.commit()
    
    



