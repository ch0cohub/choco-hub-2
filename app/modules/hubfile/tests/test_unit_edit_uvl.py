import pytest
import os
import shutil
from app import db
from app.modules.dataset.models import DataSet, DSMetaData, PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.hubfile.models import Hubfile
from dotenv import load_dotenv


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
        id=99,
        title="Test Dataset",
        description="Test Description",
        publication_type=PublicationType.JOURNAL_ARTICLE,
    )
    db.session.add(dsmetadata)
    db.session.commit()

    dataset = DataSet(id=99, user_id=1, ds_meta_data_id=dsmetadata.id)
    db.session.add(dataset)
    db.session.commit()
    # New FMMetaData for testing
    fmmetadata = FMMetaData(
        id=99,
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

    # Creación del archivo para editar
    existe = os.path.exists("uploads/user_1/dataset_99/uvl_test.uvl")
    working_dir = os.getenv("WORKING_DIR", "")
    src_folder = os.path.join(working_dir, "app", "modules", "dataset", "uvl_examples")
    dest_folder = os.path.join(
        working_dir, "uploads", f"user_{dataset.user_id}", f"dataset_{dataset.id}"
    )
    file_name = "uvl_test.uvl"
    file_path = os.path.join(dest_folder, file_name)

    if existe is False:
        load_dotenv()
        os.makedirs(dest_folder, exist_ok=True)
        shutil.copy(os.path.join(src_folder, file_name), dest_folder)

    # Create a new hubfile for testing
    new_hubfile = Hubfile(
        id=99,
        name=file_name,
        checksum="1234567890abcdeg",
        size=os.path.getsize(file_path),
        feature_model_id=feature_model.id,
    )
    db.session.add(new_hubfile)
    db.session.commit()

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
    response = test_client.post("/file/edit/99", json=edit_payload)
    assert response.status_code == 200, "El POST de edición no fue exitoso."

    # Verificar que el contenido ha sido actualizado
    response = test_client.get("/file/view/99")
    assert response.status_code == 200, "No se pudo obtener el archivo editado."
    assert (
        b"EDITADO" in response.data
    ), "El contenido del archivo no fue actualizado correctamente."
