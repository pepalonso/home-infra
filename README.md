- To activate the python virtual enviroment for installing dependencies localy

```bash
    .\venv\Scripts\Activate.ps1
```

## Run the containers

- In development

```bash
    docker-compose up

    #If any direct modification of the containers
    docker-compose up --build
```

- In production:

```bash
    docker-compose -f docker-compose.yml up --build -d
```
