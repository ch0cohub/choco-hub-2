from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token
from core.environment.host import get_host_for_locust_testing
import random


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

    @task
    def update_dataset_community(self):
        dataset_id = random.randint(1, 1000)  # IDs de prueba
        community_id = random.randint(1, 500)  # IDs de prueba

        response = self.client.post(
            "/dataset/update_community",
            json={"dataset_id": dataset_id, "community_id": community_id},
        )
        print(f"Update Dataset Community: {response.status_code} - {response.text}")

    @task
    def remove_dataset_community(self):
        dataset_id = random.randint(1, 1000)  # IDs de prueba
        community_id = random.randint(1, 500)  # IDs de prueba

        response = self.client.post(
            "/dataset/remove_community",
            json={"dataset_id": dataset_id, "community_id": community_id},
        )
        print(f"Remove Dataset Community: {response.status_code} - {response.text}")


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
