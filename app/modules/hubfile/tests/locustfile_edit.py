from locust import HttpUser, TaskSet, task, between
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token


class EditFileBehavior(TaskSet):
    def on_start(self):
        self.ensure_logged_out()
        self.login()

    @task
    def ensure_logged_out(self):
        response = self.client.get("/logout")
        if response.status_code != 200:
            print(f"Logout failed or no active session: {response.status_code}")

    @task
    def login(self):
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
        if response.status_code == 200:
            print("Login successful")
        else:
            print(f"Login failed: {response.status_code}")

    @task
    def edit_file(self):
        payload = {
            "content": """features
            Chat
                mandatory
                    Connection
                        alternative
                            "Peer 2 Peer"
                            Server
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
        headers = {"Content-Type": "application/json"}
        response = self.client.post("/file/edit/25", json=payload, headers=headers)

        if response.status_code != 200:
            print(f"Edit file failed: {response.status_code}")


class EditFileUser(HttpUser):
    tasks = [EditFileBehavior]
    wait_time = between(5, 9)
    host = get_host_for_locust_testing()
