# Testing

- For seeing the mySQL tables we can 
```bash
    docker ps
    docker exec -it <db-container> bash
    mariadb -u todo_user -p todo_db
```
- If a change has been made to the models.py then either run 
```bash
    docker ps
    docker exec -it <api_container> /bin/bash
    flask db init
    flask db migrate
    flask db upgrade
```


- To activate the python virtual enviroment for installing dependencies localy

```bash
    .\venv\Scripts\Activate.ps1
```