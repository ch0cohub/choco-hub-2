from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing

class ExploreBehavior(TaskSet):
    def on_start(self):
        self.explore()

    @task
    def explore(self):
        response = self.client.get("/explore?query=sample")
        if response.status_code != 200:
            print(f"Test failed: {response.status_code}")

class ExploreUser(HttpUser):
    tasks = [ExploreBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
