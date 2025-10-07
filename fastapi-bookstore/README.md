# fastapi-bookstore
Basic REST API built with Python + FastAPI

## Run app locally
```bash
uvicorn books:app --port=3000
```
or 
```bash
fastapi run books.py
```
or (Preferred for deployment)
```bash
python books.py
```

## Run a database container locally

### MySQL
```bash
docker run --name bookstore_database -e MYSQL_USER=admin -e MYSQL_PASSWORD=admin -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=bookstore-db -p 3306:3306 -d mysql
```

### Postgres
```bash
docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -d mysql:tag
```

## Liquibase for DB Schema changes

### Running Liquibase locally

For mysql:
`--driver=com.mysql.cj.jdbc.Driver`
`--url="jdbc:mysql://localhost:3306/bookstore-db"`

For postgres: 
`--driver=org.postgresql.Driver`
`--url="jdbc:postgresql://localhost:5432/bookstore-db"`

```bash
liquibase update --driver=org.postgresql.Driver --url="jdbc:postgresql://<DATABASE_IP>:<DATABASE_PORT>/<DATABASE>" --changeLogFile=./db/changelog/db.changelog-1.0.yaml --username=<USERNAME> --password=<PASSWORD>
```

### Using Docker
[What support does Liquibase have for Docker?](https://docs.liquibase.com/pro/integration-guide/what-support-does-liquibase-have-for-docker)

```bash
docker run -it --rm --add-host host.docker.internal:172.17.0.1 -e INSTALL_MYSQL=true -v ${PWD}/db/changelog:/liquibase/changelog liquibase --driver=com.mysql.cj.jdbc.Driver --url="jdbc:mysql://host.docker.internal:3306/bookstore-db" --changelog-file="./changelog/db.changelog-1.0.yaml" --username="admin" --password="admin" --classpath="/liquibase/changelog" validate
docker run -it --rm --add-host host.docker.internal:172.17.0.1 -e INSTALL_MYSQL=true -v ${PWD}/db/changelog:/liquibase/changelog liquibase --driver=com.mysql.cj.jdbc.Driver --url="jdbc:mysql://host.docker.internal:3306/bookstore-db" --changelog-file="./changelog/db.changelog-1.0.yaml" --username="admin" --password="admin" --classpath="/liquibase/changelog" update-sql > db/changelog/changelog.sql
```

For debugging
```bash
docker run -it --rm --add-host host.docker.internal:172.17.0.1 -e INSTALL_MYSQL=true -v ${PWD}/db/changelog:/liquibase/changelog --entrypoint bash liquibase/liquibase \
```

For validation command
```bash
docker run -it --rm --add-host host.docker.internal:172.17.0.1 -e INSTALL_MYSQL=true -v ${PWD}/db/changelog:/liquibase/changelog liquibase --driver=com.mysql.cj.jdbc.Driver --url="jdbc:mysql://host.docker.internal:3306/bookstore-db" --changelog-file="./changelog/db.changelog-1.0.yaml" --username="admin" --password="admin" validate
```