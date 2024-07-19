# Weather API

## Descrição

Este projeto implementa uma API RESTful para o gerenciamento de estações meteorológicas e seus dados históricos. A API permite a criação, leitura, atualização e exclusão (CRUD) de estações meteorológicas, além de realizar previsões de temperatura e análises estatísticas.

## Configuração do Projeto

### Requisitos

Python 3.10+<br>
PostgreSQL 12+

> requirements.txt
- Django==5.0.7
- python-decouple==3.8
- djangorestframework==3.15.2
- djangorestframework-simplejwt==5.3.1
- drf-spectacular==0.27.2
- drf-spectacular-sidecar==2024.7.1
- psycopg2==2.9.9
- pandas==2.2.2
- statsmodels==0.14.2
- lxml==5.2.2

### Instalação Manual

1. Clone o repositório (passo obrigatório manual e docker):

    ```sh
    git clone https://github.com/ElissonRodrigues/weather_api
    cd weather_api
    ```

2. Crie um ambiente virtual e ative-o:

    ```sh
    python -m venv venv
    source venv/bin/activate  # Para Linux/Mac
    venv\Scripts\activate     # Para Windows
    ```

3. Instale as dependências:

    ```sh
    pip install -r requirements.txt
    ```
4. Crie um arquivo `.env` na raiz do projeto com de acordo com o arquivo `.env.example`:

5. Configuração do Postgresql

    #### Pré-requisitos:
   - PostgreSQL instalado. Se você estiver usando um sistema operacional baseado em Unix, pode instalar o PostgreSQL com o seguinte comando: `sudo apt update && sudo apt install postgresql` no linux ou acesse "https://www.postgresql.org/download/" para mais informações sobre outros OS.
   - Acesso a um terminal ou linha de comando
   - Privilégios de administrador (se estiver em um sistema operacional baseado em Unix)


        1. Iniciar serviço do postgresql:
            ```shell
            sudo service postgresql start
            ```
        2. Criar uma nova base de dados: Primeiro, mude para o usuário postgres:
            ```shell
            sudo -i -u postgres || sudo su postgres
            ```
       
        3. Inicie o prompt de comando do PostgreSQL:

            ```shell
            psql
            ```
        4. crie a nova base de dados:
            ```shell
            CREATE DATABASE weather_db;
            ```

        Substitua `"weather_db"` pelo nome que você deseja dar à sua base de dados.
        
        3. Configurar o acesso à base de dados: Ainda no prompt de comando do PostgreSQL, crie um novo usuário e conceda a ele os privilégios necessários:
            ```shell
            CREATE USER admin WITH ENCRYPTED PASSWORD '1234';
            GRANT ALL PRIVILEGES ON DATABASE weather_db TO admin;
            \q
            exit
            ```
        Substitua `"admin"` pelo nome de usuário desejado e `"1234"` pela senha desejada.

6. Execute as migrações:

    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

7. Crie um superusuário para acessar a administração do Django:

    ```sh
    python manage.py createsuperuser
    ```

8. Para importar dados do `sinda` para a base de dados, utilize o comando customizado:

    ```sh
    python manage.py import_stations
    ```

9. Inicie o servidor em ambiente de desenvolvimento:

    ```sh
    python manage.py runserver
    ```
### Usando Docker

1. Certifique-se de que o Docker esteja <b><a href="https://docs.docker.com/engine/install/">instalado</a></b> e em execução. 

2. Certifique-se de que o arquivo `.env` foi criado na raiz do projeto com de acordo com o arquivo `.env.example`:

3. Construa e inicie os contêineres:

    ```sh
    docker-compose up -d --build
    ```

4. Acesse o shell interativo no container web:

    ```sh
    docker-compose run web /bin/bash
    ```

5. Execute os comandos de migração dentro do shell do container::

    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Crie um superusuário dentro do shell do container:

    ```sh
    python manage.py createsuperuser
    ```
7. Para importar dados do `sinda` para a base de dados, utilize o comando customizado dentro do shell do container:
    ```shell
    python manage.py import_stations
    ```
8. Por fim use o seguinte comando para sair o shell:
    ```
    exit
    ```
9. Pronto. O projeto já está configurado e funcionando

## Autenticação

A autenticação é feita utilizando JWT (JSON Web Tokens). Atualmente, o projeto possui dois tipos de tokens:

1. <b>Token Administrador:</b> Gerado a partir de um usuário administrador. Com este token, é possível acessar todas as funcionalidades da API.

2. <b>Token de Usuário:</b> Gerado a partir de um usuário comum. Este token não tem acesso a certas funcionalidades restritas a administradores.


### Gerar Token de Acesso apartir de um usuário existente

```http
POST /api/token/
```

### Renovar Token de Acesso
```http
POST /api/token/refresh/
```

### Verificar Token de Acesso
```http
POST /api/token/verify/
```

## Outros endpoints da API

- Listar Estações: `GET /api/stations/`
- Criar Estação: `POST /api/stations/create/`
- Detalhar Estação: `GET /api/stations/{id}/`
- Atualizar Estação (Usuário Adminstrador): `PUT /api/stations/{id}/`
- Deletar Estação (Usuário Admintrador): `DELETE /api/stations/{id}/`

- Listar todos os dados históricos: `GET /api/stations/historical/`
- Listar dados Históricos por Estação: `GET /api/stations/{station_id}/historical/`
- Previsão e Análise: `GET /api/stations/{station_id}/predict/` 
- Análise estatística básica: `GET /api/stations/{station_id}/analyze/`

## Criação de Usuário e Obtenção de Token

Para criar um usuário (Apenas administradores), utilize o endpoint:

```http
POST /api/users/register/
```

Exemplo de Corpo da Requisição

```json
{
  "username": "admin",
  "password": "adminpassword"
}
````

Exemplo de reposta
```json
{
  "refresh": "132343.efefefdfs",
  "access": "42232.43sfdfsfdsf",
}
```

> Uma outra forma de criar usuários é através do endereço `/admin`, exemplo: <br>http://127.0.0.1:8000/admin</b>

| Acessivel apenas para usuarios adminstradores 

### Obtenção de Token de Acesso 
Caso, você já possua um usuário adminstrador ou comum, você pode usar os seguinte endpoint:

```http
POST /api/token/
```
Exemplo de Corpo da Requisição:
```json
{
  "username": "admin",
  "password": "adminpassword"
}
````
Exemplo de reposta

```json
{
  "refresh": "132343.efefefdfs",
  "access": "42232.43sfdfsfdsf",
}
```

### Usando o Token de Acesso para utilizar Endpoints

Após obter o token de acesso, inclua-o no cabeçalho das suas requisições para acessar os endpoints. Todos os endpoints exigem autenticação.

Exemplo de uso do token de acesso para utilizar um endpoint protegido com jwt:

```python
import requests

# Obter o token de acesso primeiro
token_url = "http://127.0.0.1:8000/api/token/"
token_data = {
    "username": "django-user",
    "password": "django-password"
}

token_response = requests.post(token_url, json=token_data)
tokens = token_response.json()
access_token = tokens["access"]

# Usar o token de acesso 
url = "http://127.0.0.1:8000/api/stations/"
headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    print("Data:", data)
else:
    print("Ocorreu um erro:", response.json())

```

## Documentação da API
A documentação adicional da API está disponível no endpoint `/api/docs/` onde é possivel testar todos todas as funcionalidades desse projeto. A documentação é gerada automaticamente utilizando `drf-spectacular`.

## Licença

Distribuído sob a licença  GNU GPL. Veja <a href="https://github.com/ElissonRodrigues/weather_api/blob/main/LICENSE">`LICENSE`</a> para mais informações.

## Informações de Contato
- <b>Nome:</b> Elisson Rodrigues
- <b>Email:</b> elissonrodrigues@gmail.com
- <b>Website:</b> https://github.com/ElissonRodrigues



