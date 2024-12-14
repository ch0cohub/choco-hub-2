from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing
import random


class CommunityBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task
    def index(self):
        response = self.client.get("/community")

        if response.status_code != 200:
            print(f"Community index failed: {response.status_code}")

    @task
    def create_community(self):
        with self.client.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                csrf_token = response.cookies.get("csrf_token")
                self.client.post(
                    "/community/create",
                    data={
                        "name": f"Community {random.randint(1, 1000)}",
                        "description": "Test Description",
                        "csrf_token": csrf_token,
                    },
                )

    @task
    def create_community_and_join(self):
        with self.client.post(
            "/login",
            data={"username": "creator", "password": "testpass"},
            catch_response=True,
        ) as creator_response:
            if creator_response.status_code == 200:
                csrf_token_creator = creator_response.cookies.get("csrf_token")
                community_id = random.randint(1, 1000)
                self.client.post(
                    "/community/create",
                    data={
                        "name": f"Community {community_id}",
                        "description": "Test Description",
                        "csrf_token": csrf_token_creator,
                    },
                )

                with self.client.post(
                    "/login",
                    data={"username": "joiner", "password": "testpass"},
                    catch_response=True,
                ) as joiner_response:
                    if joiner_response.status_code == 200:
                        self.client.post(
                            "/community/join", json={"community_id": community_id}
                        )

    @task
    def create_community_and_delete(self):
        with self.client.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                community_id = random.randint(1, 1000)
                csrf_token = response.cookies.get("csrf_token")
                self.client.post(
                    "/community/create",
                    data={
                        "name": f"Community {community_id}",
                        "description": "Test Description",
                        "csrf_token": csrf_token,
                    },
                )

                self.client.post(f"/community/delete/{community_id}")

    @task
    def create_community_and_edit(self):
        with self.client.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                community_id = random.randint(1, 1000)
                csrf_token = response.cookies.get("csrf_token")
                self.client.post(
                    "/community/create",
                    data={
                        "name": f"Community {community_id}",
                        "description": "Test Description",
                        "csrf_token": csrf_token,
                    },
                )
                self.client.post(
                    f"/community/edit/{community_id}",
                    data={
                        "name": f"Updated Community {community_id}",
                        "description": "Updated Test Description",
                        "csrf_token": csrf_token,
                    },
                )

    @task
    def create_community_and_leave(self):
        with self.client.post(
            "/login",
            data={"username": "creator", "password": "testpass"},
            catch_response=True,
        ) as creator_response:
            if creator_response.status_code == 200:
                csrf_token_creator = creator_response.cookies.get("csrf_token")
                community_id = random.randint(1, 1000)
                self.client.post(
                    "/community/create",
                    data={
                        "name": f"Community {community_id}",
                        "description": "Test Description",
                        "csrf_token": csrf_token_creator,
                    },
                )

                with self.client.post(
                    "/login",
                    data={"username": "joiner", "password": "testpass"},
                    catch_response=True,
                ) as joiner_response:
                    if joiner_response.status_code == 200:
                        self.client.post(
                            "/community/join", json={"community_id": community_id}
                        )

                        self.client.post(
                            "/community/leave", json={"community_id": community_id}
                        )


class CommunityUser(HttpUser):
    tasks = [CommunityBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
