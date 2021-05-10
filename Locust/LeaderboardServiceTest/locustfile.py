from locust import HttpUser, User, task, between
from random import choice, randint

import json
import string
import uuid

CLIENT_API_ENDPOINT = "/api/Client"
AUTHETICATION_API_ENDPOINT = "/users"

class LeaderboardRow():
    def __init__(self, client_id, rating, leaderboard_id):
        self.client_id = client_id
        self.rating = rating
        self.leaderboard_id = leaderboard_id

    def toJSON(self):
        return {"ClientId": self.client_id,
                "Rating": self.rating,
                "LeaderboardId": self.leaderboard_id}

class UserModel():
    def __init__(self, password, user_name, id="", token="", refresh_token="", created_at="", updated_at="", user_id=""):
        self.id = id
        self.password = password
        self.user_name = user_name
        self.token = token
        self.refresh_token = refresh_token
        self.created_at = created_at
        self.updated_at = updated_at
        self.user_id = user_id

    def toJSON(self):
        return {"user_name": self.user_name,
                "password": self.password}
        

class LeaderboardAPIUser(HttpUser):
    wait_time = between(3, 5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.leaderboard_ids = set()
        self.client_id = str(uuid.uuid4())
        self.headers = {}

    def on_start(self):
        self.register()
        self.login()
        self.post_leaderboard_row()

    def register(self):
        username = self.random_string(6)
        password = self.random_string(6)
        self.user = UserModel(password, username)
        self.client.post(f"{AUTHETICATION_API_ENDPOINT}/register", json=self.user.toJSON())

    def login(self):
        response = self.client.post(f"{AUTHETICATION_API_ENDPOINT}/login", json=self.user.toJSON())
        self.user.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.user.token}"}

    @task()
    def post_leaderboard_row(self):
        leaderboard_row = self.new_random_leaderboard_row()
        self.leaderboard_ids.add(leaderboard_row.leaderboard_id)
        self.client.post(CLIENT_API_ENDPOINT, json=leaderboard_row.toJSON(), headers=self.headers)

    @task()
    def get_rows_paginated(self):
        if self.client_has_rows():
            leaderboard_id = self.random_leaderboard_id()
            offset = 0
            limit = 5
            self.client.get(f"{CLIENT_API_ENDPOINT}/{leaderboard_id}?offset={offset}&limit={limit}", name=CLIENT_API_ENDPOINT + "/{leaderboard_id}?offset={offset}&limit={limit}", headers=self.headers)

    @task()
    def get_row(self):
        if self.client_has_rows():
            leaderboard_id = self.random_leaderboard_id()
            self.client.get(f"{CLIENT_API_ENDPOINT}/{self.client_id}/{leaderboard_id}", name=CLIENT_API_ENDPOINT + "/{uuid}", headers=self.headers)

    @task()
    def update_row(self):
        if self.client_has_rows():
            rating = randint(100, 99999)
            leaderboard_id = self.random_leaderboard_id()
            leaderboard_row = LeaderboardRow(self.client_id, rating, leaderboard_id)
            self.client.put(CLIENT_API_ENDPOINT, json=leaderboard_row.toJSON(), headers=self.headers)

    @task()
    def delete_row(self):
        if self.client_has_rows():
            leaderboard_id = self.random_leaderboard_id()
            self.client.delete(f"{CLIENT_API_ENDPOINT}/{self.client_id}/{leaderboard_id}", name=CLIENT_API_ENDPOINT + "/{client_id}/{leaderboard_id}", headers=self.headers)
            self.leaderboard_ids.remove(leaderboard_id)
    
    @task
    def on_stop(self):
        self.stop()

    def random_leaderboard_id(self):
        if len(self.leaderboard_ids) > 0:
            return choice(list(self.leaderboard_ids))

    def random_string(self, length):
        alphanumeric = string.ascii_letters + string.digits
        return ''.join(choice(alphanumeric) for i in range(length))

    def client_has_rows(self):
        return len(self.leaderboard_ids) > 0

    def new_random_leaderboard_row(self):
        return LeaderboardRow(self.client_id, randint(100, 99999),randint(0, 250))


    

    
