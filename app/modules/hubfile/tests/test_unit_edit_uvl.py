import pytest


def test_edit_not_found(test_client):
    """
    Intenta editar un archivo que no existe.
    Devuelve error 404.
    """
    response = test_client.post("/file/edit/999")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data, "No redirige a pagina error 404."

#Este test no pasa ya que la base de datos de prueba no se llena con los ficheros de ejemplo, entonces no puedo editarlo


def test_edit_file_success(test_client):
    """
    Realiza un POST a /file/edit/27 y verifica que el POST ha sido efectuado correctamente.
    """
    # Datos para el POST
    payload = {
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

    # Realizar el POST
    response = test_client.post("/file/edit/27", json=payload)
    assert response.status_code == 200, "El POST no fue exitoso."

    # Verificar que el contenido ha sido actualizado
    response = test_client.get("/file/view/27")
    assert response.status_code == 200, "No se pudo obtener el archivo editado."
    assert b"EDITADO" in response.data, "El contenido del archivo no fue actualizado correctamente."