# Requirements
* python3
* pip3
* locust

When python3 and pip3 are install run: `pip3 install locust`

##Docker Loadtest Bridge
The test relies on a `loadtest` docker bridge being present. Run the following command to create a network bridge

`docker network create loadtest`