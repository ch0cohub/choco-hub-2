from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing


class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()

    @task
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)
        
    @task
    def download_all(self):
        with self.client.get("/dataset/download/all", stream=True) as response:

            if response.status_code == 200:
                print(f"Archivo descargado exitosamente: {response.status_code}")
            else:
                print(f"Error al descargar archivo: {response.status_code}")


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
