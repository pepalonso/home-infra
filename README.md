# Testing

- For seeing the mySQL tables we can 
```bash
    docker ps
    docker exec -it <db-container> bash
    mysql -u todo_user -p todo_db
```
- If a change has been made to the models.py then either run 