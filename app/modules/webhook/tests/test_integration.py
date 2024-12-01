from unittest.mock import patch, Mock
import pytest
from flask import url_for
from app import create_app
from app.modules.webhook.services import WebhookService
import os


@pytest.fixture(scope='module')
def app():
    app = create_app()
    app.config['SERVER_NAME'] = 'localhost'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    with app.app_context(), app.test_request_context():
        yield app


@pytest.fixture(scope='module')
def test_client(app):
    return app.test_client()


def test_webhook_deploy_integration_authorized(test_client):
    """
    Test the webhook deploy endpoint with a correct authorization token
    """
    with patch.object(WebhookService, 'get_web_container', return_value=Mock()), \
         patch.object(WebhookService, 'execute_container_command'), \
         patch.object(WebhookService, 'log_deployment'), \
         patch.object(WebhookService, 'restart_container'):

        response = test_client.post(
            url_for('webhook.deploy', _external=True),
            headers={'Authorization': f'Bearer {os.getenv("WEBHOOK_TOKEN")}'}
        )
        assert response.status_code == 200
        assert response.data == b'Deployment successful'


def test_webhook_deploy_integration_unauthorized(test_client):
    """
    Test the webhook deploy endpoint with an incorrect authorization token
    """
    response = test_client.post(
        url_for('webhook.deploy', _external=True),
        headers={'Authorization': 'Bearer wrong_token'}
    )
    assert response.status_code == 403
    assert b"Unauthorized" in response.data


def test_webhook_restart_container_integration(test_client):
    """
    Test to ensure the container is restarted 
    """
    mock_container = Mock()
    mock_container.id = 'test_container_id'
    mock_container.exec_run.return_value = (0, b'Success')  # To avoid TypeError

    with patch.object(WebhookService, 'get_web_container', return_value=mock_container), \
         patch.object(WebhookService, 'restart_container') as mock_restart:
        
        response = test_client.post(
            url_for('webhook.deploy', _external=True),
            headers={'Authorization': f'Bearer {os.getenv("WEBHOOK_TOKEN")}'},
            json={'container_id': 'test_container_id'}
        )
        
        assert response.status_code == 200
        assert mock_restart.called
        assert response.data == b'Deployment successful'
        
def test_webhook_log_deployment_integration(test_client):
    """
    Test to ensure the deployment is logged
    """
    mock_container = Mock()
    mock_container.id = 'test_container_id'
    mock_container.exec_run.return_value = (0, b'Success')  

    with patch.object(WebhookService, 'get_web_container', return_value=mock_container), \
         patch.object(WebhookService, 'log_deployment') as mock_log:
        
        response = test_client.post(
            url_for('webhook.deploy', _external=True), 
            headers={'Authorization': f'Bearer {os.getenv("WEBHOOK_TOKEN")}'},
            json={'container_id': 'test_container_id'}
        )
        
        assert response.status_code == 200
        assert mock_log.called
        assert response.data == b'Deployment successful'