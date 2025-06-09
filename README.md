- To activate the python virtual enviroment for installing dependencies localy

```bash
    .\venv\Scripts\Activate.ps1
```

## Run the containers

- In development

n8n: http://localhost:8080
Home Assistant: http://localhost:8123
Vaultwarden: http://localhost:8081
Netdata: http://localhost:19999

```bash
    docker-compose up

    #If any direct modification of the containers
    docker-compose up --build
```

- In production:

```bash
    docker-compose -f docker-compose.yml up --build -d
```
