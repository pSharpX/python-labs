CHANGELOG_DIR=$(PWD)/db/changelog
GENERATED_DIR=$(PWD)/db/changelog

DB_URL=jdbc:mysql://host.docker.internal:3306/bookstore_database
DB_USER=admin
DB_PASS=admin

test:
	pytest run

install:
	pip install -r requirements.txt

generate-sql:
	docker run --rm \
	    --add-host host.docker.internal:172.17.0.1 \
	    -e INSTALL_MYSQL=true \
		-v $(CHANGELOG_DIR):/liquibase/changelog \
		liquibase/liquibase \
		--driver=com.mysql.cj.jdbc.Driver \
		--changelog-file="./db.changelog-1.0.yaml" \
		--classpath="/liquibase/changelog" \
		--url=$(DB_URL) \
		--username=$(DB_USER) \
		--password=$(DB_PASS) \
		updateSQL > $(GENERATED_DIR)/changelog.sql

validate-sql:
	docker run --rm \
	    --add-host host.docker.internal:172.17.0.1 \
	    -e INSTALL_MYSQL=true \
		-v $(CHANGELOG_DIR):/liquibase/changelog \
		liquibase/liquibase \
		--driver=com.mysql.cj.jdbc.Driver \
		--changelog-file="./db.changelog-1.0.yaml" \
		--classpath="/liquibase/changelog" \
		--url=$(DB_URL) \
		--username=$(DB_USER) \
		--password=$(DB_PASS) \
		validate

status-sql:
	docker run --rm \
	    --add-host host.docker.internal:172.17.0.1 \
	    -e INSTALL_MYSQL=true \
		-v $(CHANGELOG_DIR):/liquibase/changelog \
		liquibase/liquibase \
		--driver=com.mysql.cj.jdbc.Driver \
		--changelog-file="./db.changelog-1.0.yaml" \
		--classpath="/liquibase/changelog" \
		--url=$(DB_URL) \
		--username=$(DB_USER) \
		--password=$(DB_PASS) \
		status

migrate:
	docker run --rm \
	    --add-host host.docker.internal:172.17.0.1 \
	    -e INSTALL_MYSQL=true \
		-v $(CHANGELOG_DIR):/liquibase/changelog \
		liquibase/liquibase \
		--driver=com.mysql.cj.jdbc.Driver \
		--changelog-file="./db.changelog-1.0.yaml" \
		--classpath="/liquibase/changelog" \
		--url=$(DB_URL) \
		--username=$(DB_USER) \
		--password=$(DB_PASS) \
		update

initialize:
	docker compose up

run:
	uvicorn app.main:app --port=3000 --reload