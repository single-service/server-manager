import json

import paramiko

# Настройки подключения
hostname = '62.109.31.156'  # Замените на адрес Вашего сервера
username = 'root'     # Замените на Ваш логин
password = 'oVkSLisg3jAxeTsn'     # Замените на Ваш пароль
port = 64022
config_path = "server_configuration.json"

CONFIG = None
with open(config_path,"r") as json_file:
    CONFIG = json.load(json_file)

# Создание SSH клиента
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def exec_comand_output(client, command: str):
    print("---------------")
    print(command)
    stdin, stdout, stderr = client.exec_command(command)
    print("|", stdout.read().decode(), "|")
    print(stderr.read().decode())
    return stdin, stdout, stderr


def create_ssh_keys(client):
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


def change_ssh_port(client, new_port):
    command = f"sudo sed -i 's/^#Port 22/Port {new_port}/' /etc/ssh/sshd_config"
    stdin, stdout, stderr = client.exec_command(command)
    stdin.write(password + '\n')  # Ввод пароля для sudo
    stdin.flush()

    # Перезапуск SSH сервиса
    client.exec_command('sudo systemctl restart sshd')

def install_docker(client):
    command = "sudo docker --version"
    stdin, stdout, stderr = client.exec_command(command)
    error = stderr.read().decode()
    if "command not found" not in error:
        print("Docker installed yet")
        return
    print("Installing docker")
    # Установка необходимых пакетов
    # install_command = "sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common"
    # stdin, stdout, stderr = client.exec_command(install_command)
    # print("---------")
    # print(install_command)
    # print("stdout:", stdout.read().decode())
    # print("stderr:", stderr.read().decode())

    # # Добавление GPG ключа для официального репозитория Docker
    # add_key_command = "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -"
    # stdin, stdout, stderr = client.exec_command(add_key_command)
    # print("---------")
    # print(add_key_command)
    # print("stdout:", stdout.read().decode())
    # print("stderr:", stderr.read().decode())

    # # Добавление репозитория Docker
    # add_repo_command = "sudo add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\""
    # stdin, stdout, stderr = client.exec_command(add_repo_command)
    # print("---------")
    # print(add_repo_command)
    # print("stdout:", stdout.read().decode())
    # print("stderr:", stderr.read().decode())

    # # Установка Docker
    # final_install_command = "sudo apt-get update && sudo apt-get install -y docker-ce"
    # stdin, stdout, stderr = client.exec_command(final_install_command)
    # print("---------")
    # print(final_install_command)
    # print("stdout:", stdout.read().decode())
    # print("stderr:", stderr.read().decode())
    # Установка Docker
    install_command = (
        "sudo apt-get update && "
        "sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common && "
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - && "
        "sudo add-apt-repository \"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable\" && "
        "DEBIAN_FRONTEND=noninteractive sudo apt-get install -y docker-ce"
    )
    stdin, stdout, stderr = client.exec_command(install_command)
    print(stdout.read().decode())
    print(stderr.read().decode())

    print("Docker installed successfully")

def set_docker_without_sudo(client):
    stdin, stdout, stderr = client.exec_command(f"sudo usermod -aG docker {username}")
    print(stdout.read().decode())
    print(stderr.read().decode())
    stdin, stdout, stderr = client.exec_command("docker --version")
    if "Docker version" in stdout.read().decode():
        print("Docker can be used without sudo")
        return
    print("Docker set rights is failed")

def swarm_init(client, config_data):
    command = "docker node ls"
    stdin, stdout, stderr = client.exec_command(command)
    if "Error response from daemon" not in stderr.read().decode():
        print("Swarm initialized yet")
    command = "docker swarm init"
    stdin, stdout, stderr = client.exec_command(command)
    response = stdout.read().decode().split("\n")
    for resp in response:
        if "docker swarm join --token " in resp:
            token_data = resp.split("docker swarm join --token ")[1]
            print(f"JOIN for swarm: docker swarm join --token {token_data}")
            break

def set_node_tag(client, tag):
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


def install_nginx(client):
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

def add_my_sshkey2authorized_keys(client, my_sshkey_path):
    with open(my_sshkey_path, 'r') as key_file:
        ssh_key = key_file.read().strip()
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

def add_node_exporter(client):
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

try:
    # Подключение к серверу
    client.connect(hostname, username=username, password=password, port=port)

    # Выполнение команд
    # create_ssh_keys(client)
    # install_docker(client)
    # set_docker_without_sudo(client)
    # swarm_init(client, CONFIG)
    # set_node_tag(client, CONFIG.get("node_tag"))
    # install_nginx(client)
    add_my_sshkey2authorized_keys(client, CONFIG.get("sshkey_path"))
    add_node_exporter(client)
    # change_ssh_port(client, 64022)
finally:
    # Отключение от сервера
    client.close()
