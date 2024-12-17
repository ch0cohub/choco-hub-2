import random
from locust import HttpUser, TaskSet, task
from core.locust.common import get_csrf_token, fake
from core.environment.host import get_host_for_locust_testing
import random


class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()
        self.signupForRating()
        self.loginForRating()

    def signupForRating(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/signup",
            data={
                "email": fake.email(),
                "password": fake.password(),
                "csrf_token": csrf_token,
            },
        )
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")

    def loginForRating(self):
        response = self.client.get("/login")
        if response.status_code != 200 or "Login" not in response.text:
            print("Already logged in or unexpected response, redirecting to logout")
            self.ensure_logged_out()
            response = self.client.get("/login")

        csrf_token = get_csrf_token(response)

        response = self.client.post(
            "/login",
            data={
                "email": "user1@example.com",
                "password": "1234",
                "csrf_token": csrf_token,
            },
        )
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")

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
    def like_dataset(self):
        # Simulating dataset liking by sending random valid values
        dataset_id = 44  # Simulate a dataset ID range
        value = random.choice([1, -1])  # Simulate liking or disliking
        headers = (
            {"X-CSRFToken": self.csrf_token} if hasattr(self, "csrf_token") else {}
        )

        with self.client.post(
            "/api/dataset/like",
            json={"dataset_id": dataset_id, "value": value},
            headers=headers,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                print(f"Total likes for dataset {dataset_id}: {data['total_likes']}")
            else:
                print(
                    f"Error liking dataset {dataset_id}: {response.status_code} - {response.text}"
                )

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
