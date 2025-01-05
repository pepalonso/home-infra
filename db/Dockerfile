FROM mariadb:latest
RUN apt update && apt install -y mariadb-client

# Copy custom my.cnf to the MariaDB configuration directory
COPY my.cnf /etc/mysql/my.cnf