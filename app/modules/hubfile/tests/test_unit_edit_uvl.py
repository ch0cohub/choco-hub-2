import pytest
from app import db
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.hubfile.models import Hubfile


def test_edit_not_found(test_client):
    """
    Intenta editar un archivo que no existe.
    Devuelve error 404.
    """
    response = test_client.post("/file/edit/999")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data, "No redirige a pagina error 404."


def test_edit_file_success(test_client):

    # New DSMetaData y DataSet for testing
    dsmetadata = DSMetaData(
        id=3,
        title="Test Dataset",
        description="Test Description",
        publication_type=PublicationType.JOURNAL_ARTICLE,
    )
    db.session.add(dsmetadata)
    db.session.commit()

    dataset = DataSet(id=1, user_id=1, ds_meta_data_id=dsmetadata.id)
    db.session.add(dataset)
    db.session.commit()
    # New FMMetaData for testing
    fmmetadata = FMMetaData(
        id=3,
        uvl_filename="file1.uvl",
        title="Feature Model 1",
        description="Description for feature model 1",
        publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
    )
    db.session.add(fmmetadata)
    db.session.commit()
    # Create a new DSMetaData and DataSet to use as a foreign key before creating a new FeatureModel
    feature_model = FeatureModel(
        id=101, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
    )
    db.session.add(feature_model)
    db.session.commit()
    # Create a new hubfile for testing
    new_hubfile = Hubfile(
        id=1,
        name="file1.uvl",
        checksum="1234567890abcdeg",
        size=1024,
        feature_model_id=feature_model.id,
    )
    db.session.add(new_hubfile)
    db.session.commit

    """
    Realiza un POST a /file/edit/1 y verifica que el POST ha sido efectuado correctamente.
    """
    # Datos para el POST
    edit_payload = {
        "content": """features
        Chat
            mandatory
                Connection
                    alternative
                        "Peer 2 Peer"
                        EDITADO
                Messages
                    or
                        Audios
            optional
                "Data Storage"
                "Media Player"

        constraints
            Server => "Data Storage"
            Video | Audio => "Media Player"
        """
    }

    # Realizar el POST para editar el archivo
    response = test_client.post("/file/edit/1", json=edit_payload)
    assert response.status_code == 200, "El POST de edición no fue exitoso."

    # Verificar que el contenido ha sido actualizado
    response = test_client.get("/file/view/1")
    assert response.status_code == 200, "No se pudo obtener el archivo editado."
    assert b"EDITADO" in response.data, "El contenido del archivo no fue actualizado correctamente."
