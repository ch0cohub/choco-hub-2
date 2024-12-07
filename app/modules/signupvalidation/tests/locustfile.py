from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token, fake


class SignupvalidationBehavior(TaskSet):
    def on_start(self):
        self.index()

    @task
    def signup_invalido(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/signup", data={
            "email": " ",
            "password": fake.password(),
            "csrf_token": csrf_token
        })
        if response.status_code == 200:
            assert "This field is required" in response.text, "Expected error message not found"
            print(f"Signup failed with status code {response.status_code} as expected")
        else:
            print(f"Signup failed with unexpected status code: {response.status_code}")
    @task      
    def signup_valido(self):
        response = self.client.get("/signup")
        csrf_token = get_csrf_token(response)

        response = self.client.post("/signup", data={
            "email": fake.email(),
            "password": fake.password(),
            "csrf_token": csrf_token
        })
        if response.status_code != 200:
            print(f"Signup failed: {response.status_code}")
            


@task
def signup_con_email_repetido(self):
    # Primer registro de usuario con un correo válido
    response = self.client.get("/signup")
    csrf_token = get_csrf_token(response)  # Función que obtiene el CSRF token de la respuesta

    email = fake.email()
    password = fake.password()

    # Registramos el primer usuario con el correo
    response = self.client.post("/signup", data={
        "email": email,  # Correo de usuario
        "password": password,  # Contraseña generada de manera aleatoria
        "csrf_token": csrf_token
    })

    # Verificar que el primer registro fue exitoso (código 200 y sin error de validación)
    if response.status_code == 200:
        print("First signup successful.")
    else:
        print(f"Signup failed for first user: {response.status_code}")

    # Segundo intento de registro con el mismo correo
    response = self.client.post("/signup", data={
        "email": email,  # Intentamos con el mismo correo
        "password": fake.password(),  # Nueva contraseña generada
        "csrf_token": csrf_token
    })

    # Verificar que el segundo intento de registro falla
    if response.status_code == 200:
        assert "Email already in use" in response.text, "Expected error message for duplicate email not found"
        print(f"Signup failed as expected for email {email}: {response.status_code}")
    else:
        print(f"Unexpected status code: {response.status_code}")

            
            


class SignupvalidationUser(HttpUser):
    tasks = [SignupvalidationBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
