CHANGELOG_DIR=$(PWD)/liquibase
GENERATED_DIR=$(PWD)/generated

DB_URL=jdbc:postgresql://localhost:5432/app_db
DB_USER=postgres_user
DB_PASS=postgres_pass

test:
	pytest run

install:
	pip install -r requirements.txt

generate-sql:
	docker run --rm \
		-v $(CHANGELOG_DIR):/liquibase/changelog \
		liquibase/liquibase \
		--changeLogFile=./db/changelog/db.changelog-1.0.yaml \
		--url=$(DB_URL) \
		--username=$(DB_USER) \
		--password=$(DB_PASS) \
		updateSQL > $(GENERATED_DIR)/schema.sql

migrate:
	docker run --rm \
		-v $(CHANGELOG_DIR):/liquibase/changelog \
		$(LIQUIBASE_IMAGE) \
		--changeLogFile=/liquibase/changelog/changelog.xml \
		--url=$(DB_URL) \
		--username=$(DB_USER) \
		--password=$(DB_PASS) \
		update

initialize:
	docker compose up

run:
	uvicorn app.main:app --port=3000 --reload