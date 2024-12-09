from portainer_py import portainer_for_host

PORTAINER_URL = "http://0.0.0.0:9002"
PORTAINER_USERNAME = "admin"
PORTAINER_PASSWORD = "45ROS_!_hen25"

portainer = portainer_for_host(PORTAINER_URL)
portainer.login(PORTAINER_USERNAME, PORTAINER_PASSWORD)
endpoints = portainer.endpoints()
print(endpoints)
# stack = portainer.stack_with_name("my-stack")