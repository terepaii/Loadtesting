from locust import HttpUser, User, task, between
from random import choice, randint

import json
import uuid

CLIENT_API_ENDPOINT = "/api/Client"

class LeaderboardRow():
    def __init__(self, client_id, rating, leaderboard_id):
        self.client_id = client_id
        self.rating = rating
        self.leaderboard_id = leaderboard_id

    def toJSON(self):
        return {"ClientId": self.client_id,
                "Rating": self.rating,
                "LeaderboardId": self.leaderboard_id}

class LeaderboardAPIUser(HttpUser):
    wait_time = between(3, 5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.leaderboard_ids = set()
        self.client_id = str(uuid.uuid4())

    def on_start(self):
       self.post_leaderboard_row()
       
    @task()
    def post_leaderboard_row(self):
        leaderboard_row = self.new_random_leaderboard_row()
        self.leaderboard_ids.add(leaderboard_row.leaderboard_id)
        self.client.post(CLIENT_API_ENDPOINT, json=leaderboard_row.toJSON())

    @task()
    def get_rows_paginated(self):
        if self.client_has_rows():
            leaderboard_id = self.random_leaderboard_id()
            offset = 0
            limit = 5
            self.client.get(f"{CLIENT_API_ENDPOINT}/{leaderboard_id}?offset={offset}&limit={limit}", name=CLIENT_API_ENDPOINT + "/{leaderboard_id}?offset={offset}&limit={limit}")

    @task()
    def get_row(self):
        if self.client_has_rows():
            leaderboard_id = self.random_leaderboard_id()
            self.client.get(f"{CLIENT_API_ENDPOINT}/{self.client_id}/{leaderboard_id}", name=CLIENT_API_ENDPOINT + "/{uuid}")

    @task()
    def update_row(self):
        if self.client_has_rows():
            rating = randint(100, 99999)
            leaderboard_id = self.random_leaderboard_id()
            leaderboard_row = LeaderboardRow(self.client_id, rating, leaderboard_id)
            self.client.put(CLIENT_API_ENDPOINT, json=leaderboard_row.toJSON())

    @task()
    def delete_row(self):
        if self.client_has_rows():
            leaderboard_id = self.random_leaderboard_id()
            self.client.delete(f"{CLIENT_API_ENDPOINT}/{self.client_id}/{leaderboard_id}", name=CLIENT_API_ENDPOINT + "/{client_id}/{leaderboard_id}")
            self.leaderboard_ids.remove(leaderboard_id)
    
    @task
    def on_stop(self):
        self.stop()

    def random_leaderboard_id(self):
        if len(self.leaderboard_ids) > 0:
            return choice(list(self.leaderboard_ids))

    def client_has_rows(self):
        return len(self.leaderboard_ids) > 0

    def new_random_leaderboard_row(self):
        return LeaderboardRow(self.client_id, randint(100, 99999),randint(0, 250))


    

    
