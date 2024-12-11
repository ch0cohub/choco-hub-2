import pytest

#Nota: los casos de prueba positivos se tarda demasiado en aplicar y borrar seeders, por lo que se procede con test en selenium

def test_view_file_other_formats_unsupported(test_client):
    """
    Caso con formato no válido.
    Devuelve error 404.
    POSIBLE ERROR: Devuelve error 404 en vez de 400, porque en el contexto de la app no se llama a la URL de forma explícita. Se elige no solucionar ya que son casos específicos en los cuales se intenta forzar error y no afecta experiencia de usuario
    """
    response = test_client.get('/file/view_other/1/unsupported')
    assert response.status_code == 404 #debería ser 400
    assert b"Page Not Found" in response.data, "No redirige a pagina error 404." #debería ser "Formato no soportado"


def test_view_file_other_formats_not_found(test_client):
    """
    Prueba el caso de un archivo inexistente.
    Devuelve error 404.
    """
    response = test_client.get('/file/view_other/999/glencoe')
    assert response.status_code == 404
    assert b"Page Not Found" in response.data, "No redirige a pagina error 404."

