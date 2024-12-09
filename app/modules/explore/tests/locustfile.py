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
    # locust functiona de la siguiente manera: la clase ExploreUser tiene una lista de tareas "tasks" de ti ExploreBehavior, que
    # hereda de TaskSet. ExploreBehavior tiene un método "explore" que hace una petición GET a la ruta "/explore?query=sample".
    # "host" es simplemente la dirección del servidor que se va a probar. 
    tasks = [ExploreBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
