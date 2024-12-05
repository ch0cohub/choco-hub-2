import pytest
from flask import url_for
from app import create_app
from app.modules.webhook.services import WebhookService
from unittest.mock import patch, Mock
import docker
import subprocess
import os


@pytest.fixture(scope='module')
def app(self):
    app = create_app()
    app.config['SERVER_NAME'] = 'localhost'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    with app.app_context(), app.test_request_context():
        self.assertEqual('/', url_for('root.home'))
        yield app
             

@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


def test_sample_assertion(test_client):
    """
    Sample test to verify that the test framework and environment are working correctly.
    It does not communicate with the Flask application; it only performs a simple assertion to
    confirm that the tests in this module can be executed.
    """
    greeting = "Hello, World!"
    assert greeting == "Hello, World!", "The greeting does not coincide with 'Hello, World!'"


def test_webhook_deploy_authorized(test_client):
    """
    Test that the /webhook/deploy endpoint works with the correct authorization token.
    """
    test_client.application.config['SERVER_NAME'] = 'localhost'
    
    with test_client.application.app_context():
        #patch para simular dependencias externas como Docker
        with patch.object(WebhookService, 'get_web_container', return_value='web_container_mock'), \
             patch.object(WebhookService, 'execute_container_command'), \
             patch.object(WebhookService, 'log_deployment'), \
             patch.object(WebhookService, 'restart_container'):

            response = test_client.post(
                url_for('webhook.deploy', _external=True), # external=True para obtener la URL completa
                headers={'Authorization': f'Bearer {os.getenv("WEBHOOK_TOKEN")}'}
            )
            assert response.status_code == 200
            assert response.data == b'Deployment successful'


def test_webhook_deploy_unauthorized(test_client):
    """
    Test that the /webhook/deploy endpoint returns 403 when the authorization token is incorrect.
    """
    test_client.application.config['SERVER_NAME'] = 'localhost'
    
    # No necesitamos el app_context ya que test_client maneja automáticamente el contexto de la solicitud
    response = test_client.post(
        url_for('webhook.deploy', _external=True),  
        headers={'Authorization': 'Bearer wrong_token'}
    )

    assert response.status_code == 403
    assert b"Unauthorized" in response.data
    

def test_get_volume_name():
    """
    Test get_volume_name to ensure it returns the correct volume or raises an error if not found.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.attrs = {
        'Mounts': [
            {'Destination': '/app', 'Name': 'volume_name_mock'}
        ]
    }

    # Positive case: Volume found
    volume_name = service.get_volume_name(mock_container)
    assert volume_name == 'volume_name_mock'

    # Failed case: Volume not found
    mock_container.attrs = {'Mounts': []}
    with pytest.raises(ValueError) as exception_info:
        service.get_volume_name(mock_container)
    assert "No volume or bind mount found mounted on /app" in str(exception_info.value)


def test_execute_host_command():
    """
    Test execute_host_command to ensure it runs the command or aborts if it fails.
    """
    service = WebhookService()
    volume_name = 'test_volume'
    command = ['ls', '-la']

    # Positive case: Command correctly executed 
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = None  # Simula que el comando se ejecutó sin error
        service.execute_host_command(volume_name, command)
        mock_run.assert_called_once_with([
            'docker', 'run', '--rm', '-v', f'{volume_name}:/app',
            '-v', '/var/run/docker.sock:/var/run/docker.sock', '-w', '/app', *command
        ], check=True)

    # Failed case: Error on command execution
    with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, command)) as mock_run:
        with pytest.raises(Exception) as excinfo:
            service.execute_host_command(volume_name, command)
        assert "Host command failed" in str(excinfo.value)


def test_execute_container_command():
    """
    Test execute_container_command to ensure it runs the command inside a container or aborts if it fails.
    """
    service = WebhookService()
    mock_container = Mock()
    command = ['echo', 'Hello']

    # Positive case: Command correctly executed inside the container
    mock_container.exec_run.return_value = (0, b'Hello\n')
    output = service.execute_container_command(mock_container, command)
    assert output == 'Hello\n'

    # Failed case: Error on command execution inside the container
    mock_container.exec_run.return_value = (1, b'Error')
    with pytest.raises(Exception) as excinfo:
        service.execute_container_command(mock_container, command)
    assert "Container command failed: Error" in str(excinfo.value)


def test_log_deployment():
    """
    Test log_deployment to ensure it writes the correct log entry inside the container.
    """
    service = WebhookService()
    mock_container = Mock()
    with patch('app.modules.webhook.services.WebhookService.execute_container_command') as mock_execute:
        service.log_deployment(mock_container)
        assert mock_execute.called
        assert "echo \"Deployment successful at" in mock_execute.call_args[0][1]


def test_restart_container():
    """
    Test restart_container to ensure it calls the correct script with the container ID.
    """
    service = WebhookService()
    mock_container = Mock()
    mock_container.id = 'test_container_id'

    with patch('subprocess.Popen') as mock_popen:
        service.restart_container(mock_container)
        mock_popen.assert_called_once_with(["/bin/sh", "/app/scripts/restart_container.sh", 'test_container_id'])
