import socket
import time

from django.conf import settings

import paramiko
import requests

from docker_service.models import Node

class NodeProcessor:

    def __init__(self, node: Node):
        self.node: Node = node

    def prepare_node(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                self.node.ssh_host,
                username=self.node.ssh_username,
                password=self.node.ssh_password,
                port=self.node.current_ssh_port
            )
            self._create_ssh_keys(client)
            self._install_docker(client)
            self._set_docker_without_sudo(client)
            if self.node.is_main:
                if not self.node.join_swarm_string:
                    swarm_token = self._swarm_init(client)
                    if swarm_token:
                        self.node.join_swarm_string = swarm_token
                        self.node.save()
                self._install_nginx(client)
            else:
                # TODO add join swarm
                pass
            self._set_node_tag(client, self.node.tag)
            self._add_my_sshkey2authorized_keys(client, self.node.ssh_public_key)
            # self._add_node_exporter(client)
            self._manage_server_directories_and_services(client)
            if self.node.current_ssh_port != self.node.new_ssh_port:
                self._change_ssh_port(client, self.node.current_ssh_port, self.node.new_ssh_port)
                self.node.current_ssh_port = self.node.new_ssh_port
                self.node.save()
            if self.node.is_main:
                self._add_node2_portainer(client)
        except Exception as e:
            return False, str(e)
        finally:
            # Отключение от сервера
            client.close()
        return True, None

    def _create_ssh_keys(self, client):
        # Проверяем наличие файла id_rsa.pub
        stdin, stdout, stderr = client.exec_command('test -f ~/.ssh/id_rsa.pub && echo "exists" || echo "not exists"')
        file_status = stdout.read().decode()
        print("file status", file_status)
        if "not exists" in file_status:
            print("Файл id_rsa.pub не найден. Выполняем ssh-keygen...")
            # Выполняем ssh-keygen
            stdin, stdout, stderr = client.exec_command('ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -N ""')
            print("stdout", stdout.read().decode())
            print("stderr", stderr.read().decode())
        else:
            print("Файл id_rsa.pub уже существует.")


    def _change_ssh_port(self, client, old_port, new_port):
        command = f"sudo sed -i 's/^#Port {old_port}/Port {new_port}/' /etc/ssh/sshd_config"
        stdin, stdout, stderr = client.exec_command(command)
        stdin.write(self.node.ssh_password + '\n')  # Ввод пароля для sudo
        stdin.flush()

        # Перезапуск SSH сервиса
        client.exec_command('sudo systemctl restart sshd')

    def _install_docker(self, client):
        command = "sudo docker --version"
        stdin, stdout, stderr = client.exec_command(command)
        stdin.write(self.node.ssh_password + '\n')  # Ввод пароля для sudo
        stdin.flush()

        error = stderr.read().decode()
        print("Docker version check error: ", stderr.read().decode())
        print("Docker version check out: ", stdout.read().decode())
        if "command not found" not in error:
            print("Docker installed yet")
            return
        print("Installing docker")
        # Установка Docker
        install_command = (
            "sudo apt-get update && "
            "sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common && "
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && "
            "sudo add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" && "
            "DEBIAN_FRONTEND=noninteractive sudo apt-get install -y docker-ce"
        )
        stdin, stdout, stderr = client.exec_command(install_command)
        stdin.write(self.node.ssh_password + '\n')  # Ввод пароля для sudo
        stdin.flush()
        print("Docker install error: ", stderr.read().decode())
        print("Docker install out: ", stdout.read().decode())

        print("Docker installed successfully")

    def _set_docker_without_sudo(self, client):
        stdin, stdout, stderr = client.exec_command(f"sudo usermod -aG docker {self.node.ssh_password}")
        print(stdout.read().decode())
        print(stderr.read().decode())
        stdin, stdout, stderr = client.exec_command("docker --version")
        if "Docker version" in stdout.read().decode():
            print("Docker can be used without sudo")
            return
        print("Docker set rights is failed")

    def _swarm_init(self, client):
        command = "docker node ls"
        stdin, stdout, stderr = client.exec_command(command)
        if "Error response from daemon" not in stderr.read().decode():
            print("Swarm initialized yet")
            return
        command = "docker swarm init"
        stdin, stdout, stderr = client.exec_command(command)
        response = stdout.read().decode().split("\n")
        for resp in response:
            if "docker swarm join --token " in resp:
                token_data = resp.split("docker swarm join --token ")[1]
                print(f"JOIN for swarm: docker swarm join --token {token_data}")
                break
        return token_data

    def _set_node_tag(self, client, tag):
        command = "docker node ls"
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode().split("\n")[1:-1]
        for line in output:
            if "*" in line:
                line = line.split("   ")
                current_host = line[1]
                break
        command = f'docker node update --label-add tag={tag} {current_host}'
        stdin, stdout, stderr = client.exec_command(command)
        print(f"Тег для ноды {current_host} обновлен на {tag}.")


    def _install_nginx(self, client):
        commands = [
            "sudo apt update",
            "sudo apt install -y nginx",
            "sudo apt install -y certbot python3-certbot-nginx"
        ]
        for command in commands:
            _, stdout, stderr = client.exec_command(command)
            print("--------")
            print(command)
            print("stdout:", stdout.read().decode())
            print("~~~~")
            print("stderr:", stderr.read().decode())

    def _add_my_sshkey2authorized_keys(self, client, ssh_key):
        _, stdout, _ = client.exec_command("cat ~/.ssh/authorized_keys")
        authorized_keys = stdout.read().decode().split("\n")
        is_exist = False
        for line in authorized_keys:
            if ssh_key in line:
                is_exist = True
                break
        if is_exist:
            print("SSH Key added already")
            return
        stdin, stdout, stderr = client.exec_command('echo "{}" >> ~/.ssh/authorized_keys'.format(ssh_key))
        if stderr.read():
            print("Ошибка при добавлении ключа:", stderr.read().decode())
        else:
            print("Ключ успешно добавлен в authorized_keys.")

    def _add_node_exporter(self, client):
        # Проверяем, запущен ли node_exporter
        stdin, stdout, stderr = client.exec_command("docker ps --filter 'name=node_exporter' --format '{{.Names}}'")
        running_containers = stdout.read().decode().strip().splitlines()
        if "node_exporter" in running_containers:
            print("Node Exporter уже запущен.")
            return

        # Если не запущен, запускаем node_exporter
        command = "docker run -d --name=node_exporter -p 9100:9100 prom/node-exporter"
        stdin, stdout, stderr = client.exec_command(command)
        print("stdout:", stdout.read().decode())
        print("stderr:", stderr.read().decode())
        print("Node Exporter запущен.")

    def _manage_server_directories_and_services(self, ssh_client: paramiko.SSHClient):
        # 1) Проверка существования папки /apps
        stdin, stdout, stderr = ssh_client.exec_command('if [ ! -d /apps ]; then mkdir /apps; fi')
        
        # 2) Проверка существования папки /apps/metrics_services
        stdin, stdout, stderr = ssh_client.exec_command('if [ ! -d /apps/metrics_services ]; then mkdir /apps/metrics_services; fi')
        
        # 3). Проверка наличия docker-compose.yml и копирование, если его нет
        remote_file_path = '/apps/metrics_services/docker-compose.yml'
        local_file_path = f"{settings.BASE_DIR}/docker_service/data/docker-compose.yml"
        sftp = ssh_client.open_sftp()
        try:
            sftp.stat(remote_file_path)
        except FileNotFoundError:
            sftp.put(local_file_path, remote_file_path)
        
        # 4) Проверка, поднят ли стэк в docker swarm - metrics_service
        stdin, stdout, stderr = ssh_client.exec_command('docker stack ls | grep metrics_service || docker stack deploy -c /apps/metrics_services/docker-compose.yml metrics_service')
        print("Execute metrics stack out: ", stdout.read().decode())
        print("Execute metrics stack error: ", stderr.read().decode())

    # Всякие функции
    def _ping_port(self, host, port, timeout=180):
        """Проверяет доступность порта на хосте."""
        end_time = time.time() + timeout
        while time.time() < end_time:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    return True
            time.sleep(1)
        return False
    
    def _get_portainer_token(self):
        """Получает токен авторизации для Portainer."""
        response = requests.post(f"{settings.PORTAINER_URL}/api/auth",
                                 json={"username": settings.PORTAINER_USERNAME, "password": settings.PORTAINER_PASSWORD})
        if response.status_code == 200:
            return response.json().get("jwt")
        else:
            raise Exception("Ошибка авторизации в Portainer: " + response.text)

    def _check_environment_exists(self, token, environment_name):
        """Проверяет наличие окружения в Portainer."""
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{settings.PORTAINER_URL}/api/endpoints", headers=headers)
        if response.status_code == 200:
            environments = response.json()
            for env in environments:
                if env["Name"] == environment_name:
                    return True
        return False

    def _create_environment(self, token, environment_name):
        """Создает новое окружение в Portainer."""
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "Name": environment_name,
            "EndpointCreationType": 2,
            "URL": f"{self.node.ssh_host}:9001"
            # Добавьте другие параметры окружения, если необходимо
        }
        response = requests.post(f"{settings.PORTAINER_URL}/api/endpoints", headers=headers, json=data)
        if response.status_code != 201:
            raise Exception("Ошибка создания окружения в Portainer: " + response.text)

    def _add_node2_portainer(self, ssh_client):
        port = 9001
        # Шаг 1: Пинг до порта 9001
        if not self._ping_port(self.node.ssh_host, port):
            raise Exception("Ошибка: порт 9001 недоступен")
        # Шаг 2: Авторизация в Portainer
        print("Portainer Agent is Ready")
        token = self._get_portainer_token()
        print("Portainer token accepted")
        # Шаг 3: Проверка существования окружения
        environment_name = str(self.node.id)
        if not self._check_environment_exists(token, environment_name):
            print("Окружения пока нет")
            # Шаг 4: Если окружение не существует, создаем его
            self._create_environment(token, environment_name)
            print("Окружение создано")
        else:
            print("Окружение уже существует")
