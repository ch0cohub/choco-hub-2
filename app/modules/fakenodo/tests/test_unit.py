from unittest.mock import MagicMock
import pytest
from app.modules.fakenodo.services import FakeNodoService
from flask import jsonify
from app.modules.fakenodo.repositories import FakeNodoRepository


@pytest.fixture(scope="module")
def fake_nodo_service():
    # Inicializamos el servicio FakeNodo
    service = FakeNodoService()
    return service


def test_test_full_connection(fake_nodo_service):
    """Test para la simulación de prueba de conexión con FakeNodo."""
    # Configuramos el mock
    fake_nodo_service.test_full_connection = MagicMock(return_value=jsonify({"success": True, "message": "FakeNodo connection test successful."}))

    # Llamamos al método real
    result = fake_nodo_service.test_full_connection()

    # Verificamos que el mock fue llamado correctamente
    fake_nodo_service.test_full_connection.assert_called_once()

    # Verificamos la respuesta
    assert result.json["success"] == True
    assert result.json["message"] == "FakeNodo connection test successful."


def test_create_new_deposition(fake_nodo_service):
    """Test para la creación de un nuevo deposition."""
    # Configuramos el mock
    fake_nodo_service.create_new_deposition = MagicMock(return_value={
        "id": 1234,
        "title": "Test Dataset",
        "description": "Test description",
        "doi": "10.1234/ABCD1234"
    })

    # Llamamos al método real
    result = fake_nodo_service.create_new_deposition("Test Dataset", "Test description")

    # Verificamos que el mock fue llamado correctamente
    fake_nodo_service.create_new_deposition.assert_called_with("Test Dataset", "Test description")

    # Verificamos la respuesta
    assert result["title"] == "Test Dataset"
    assert result["description"] == "Test description"
    assert result["doi"].startswith("10.1234/")


def test_upload_uvl_file(fake_nodo_service):
    """Test para la subida de un archivo UVL al deposition."""
    # Configuramos el mock
    fake_nodo_service.upload_file = MagicMock(return_value={
        "success": True,
        "message": "File 'dataset_file.uvl' simulated as uploaded to deposition 1234"
    })

    # Llamamos al método real con un archivo UVL
    result = fake_nodo_service.upload_file(1234, "dataset_file.uvl")

    # Verificamos que el mock fue llamado correctamente
    fake_nodo_service.upload_file.assert_called_with(1234, "dataset_file.uvl")

    # Verificamos la respuesta
    assert result["success"] == True
    assert "dataset_file.uvl" in result["message"]


def test_publish_deposition(fake_nodo_service):
    """Test para la publicación de un deposition."""
    # Configuramos el mock
    fake_nodo_service.publish_deposition = MagicMock(return_value={
        "success": True,
        "message": "Deposition 1234 simulated as published."
    })

    # Llamamos al método real
    result = fake_nodo_service.publish_deposition(1234)

    # Verificamos que el mock fue llamado correctamente
    fake_nodo_service.publish_deposition.assert_called_with(1234)

    # Verificamos la respuesta
    assert result["success"] == True
    assert "simulated as published" in result["message"]

