from flask import current_app
from locust import HttpUser, TaskSet, task
from app.modules.auth.models import User
from app.modules.dataset.models import DSMetaData, DataSet, PublicationType
from core.environment.host import get_host_for_locust_testing
from app import create_app, db


class FlamapyBehavior(TaskSet):
    def on_start(self):
        # Inicializar la aplicación Flask
        
        app = create_app()
        
        with app.app_context():
            self.dataset_id = self.create_test_dataset()
        self.index()

    def create_test_dataset(self):
        dataset = DataSet.query.first()
        return dataset.id

   

    @task
    def index(self):
        response = self.client.get("/flamapy")

        if response.status_code != 200:
            print(f"Flamapy index failed: {response.status_code}")
    
    @task
    def download_glencoe(self):
       
        response = self.client.get(f"/flamapy/download/GLENCOE/{self.dataset_id}")

        if response.status_code != 200:
            print(f"GLENCOE download failed: {response.status_code}")
        else:
            print(f"GLENCOE download successful")
    
    
    @task
    def download_splot(self):
       
        response = self.client.get(f"/flamapy/download/SPLOT/{self.dataset_id}")

        if response.status_code != 200:
            print(f"SPLOT download failed: {response.status_code}")
        else:
            print(f"SPLOT download successful")
    
    
    @task
    def download_dimacs(self):
       
        response = self.client.get(f"/flamapy/download/DIMACS/{self.dataset_id}")

        if response.status_code != 200:
            print(f"DIMACS download failed for dataset 51: {response.status_code}")
        else:
            print(f"DIMACS download successful for dataset 51")


class FlamapyUser(HttpUser):
    tasks = [FlamapyBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
