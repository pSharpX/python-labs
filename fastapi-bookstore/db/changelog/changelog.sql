-- Checksum verified. Installing mysql-connector-java-8.0.30.jar to /liquibase/lib/
-- mysql-connector-java-8.0.30.jar successfully installed in classpath.
--  Create Database Lock Table
CREATE TABLE bookstore_database.DATABASECHANGELOGLOCK (ID INT NOT NULL, `LOCKED` TINYINT NOT NULL, LOCKGRANTED datetime NULL, LOCKEDBY VARCHAR(255) NULL, CONSTRAINT PK_DATABASECHANGELOGLOCK PRIMARY KEY (ID));

--  Initialize Database Lock Table
DELETE FROM bookstore_database.DATABASECHANGELOGLOCK;

INSERT INTO bookstore_database.DATABASECHANGELOGLOCK (ID, `LOCKED`) VALUES (1, 0);

--  Lock Database
UPDATE bookstore_database.DATABASECHANGELOGLOCK SET `LOCKED` = 1, LOCKEDBY = '185f7299214c (172.17.0.2)', LOCKGRANTED = NOW() WHERE ID = 1 AND `LOCKED` = 0;

--  Create Database Change Log Table
CREATE TABLE bookstore_database.DATABASECHANGELOG (ID VARCHAR(255) NOT NULL, AUTHOR VARCHAR(255) NOT NULL, FILENAME VARCHAR(255) NOT NULL, DATEEXECUTED datetime NOT NULL, ORDEREXECUTED INT NOT NULL, EXECTYPE VARCHAR(10) NOT NULL, MD5SUM VARCHAR(35) NULL, `DESCRIPTION` VARCHAR(255) NULL, COMMENTS VARCHAR(255) NULL, TAG VARCHAR(255) NULL, LIQUIBASE VARCHAR(20) NULL, CONTEXTS VARCHAR(255) NULL, LABELS VARCHAR(255) NULL, DEPLOYMENT_ID VARCHAR(10) NULL);

--  *********************************************************************
--  Update Database Script
--  *********************************************************************
--  Change Log: ./db.changelog-1.0.yaml
--  Ran at: 2/25/26, 3:55 AM
--  Against: admin@172.20.0.1@jdbc:mysql://host.docker.internal:3306/bookstore_database
--  Liquibase version: 5.0.1
--  *********************************************************************

--  Changeset db.changelog-1.0.yaml::create-authors-table::christian.rivera
--  add authors table definition
CREATE TABLE bookstore_database.authors (id BIGINT AUTO_INCREMENT NOT NULL, name VARCHAR(30) NOT NULL, fullname VARCHAR(100) NULL, CONSTRAINT PK_AUTHORS PRIMARY KEY (id));

INSERT INTO bookstore_database.DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, MD5SUM, `DESCRIPTION`, COMMENTS, EXECTYPE, CONTEXTS, LABELS, LIQUIBASE, DEPLOYMENT_ID) VALUES ('create-authors-table', 'christian.rivera', 'db.changelog-1.0.yaml', NOW(), 1, '9:45d6ce80fc4000e614ca2261813fe4ae', 'createTable tableName=authors', 'add authors table definition', 'EXECUTED', NULL, NULL, '5.0.1', '1991757644');

--  Changeset db.changelog-1.0.yaml::create-categories-table::christian.rivera
--  add categories table definition
CREATE TABLE bookstore_database.categories (id BIGINT AUTO_INCREMENT NOT NULL, name VARCHAR(30) NOT NULL, `description` VARCHAR(1000) NULL, CONSTRAINT PK_CATEGORIES PRIMARY KEY (id));

INSERT INTO bookstore_database.DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, MD5SUM, `DESCRIPTION`, COMMENTS, EXECTYPE, CONTEXTS, LABELS, LIQUIBASE, DEPLOYMENT_ID) VALUES ('create-categories-table', 'christian.rivera', 'db.changelog-1.0.yaml', NOW(), 2, '9:98a8be9297d77c627f52fd838b4bbb65', 'createTable tableName=categories', 'add categories table definition', 'EXECUTED', NULL, NULL, '5.0.1', '1991757644');

--  Changeset db.changelog-1.0.yaml::create-books-table::christian.rivera
--  add books table definition
CREATE TABLE bookstore_database.books (id BIGINT AUTO_INCREMENT NOT NULL, author_id BIGINT NOT NULL, category_id BIGINT NOT NULL, title VARCHAR(100) NOT NULL, `description` VARCHAR(1000) NULL, rating FLOAT NOT NULL, published_date INT NOT NULL, CONSTRAINT PK_BOOKS PRIMARY KEY (id));

INSERT INTO bookstore_database.DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, MD5SUM, `DESCRIPTION`, COMMENTS, EXECTYPE, CONTEXTS, LABELS, LIQUIBASE, DEPLOYMENT_ID) VALUES ('create-books-table', 'christian.rivera', 'db.changelog-1.0.yaml', NOW(), 3, '9:7eaffb2ab5a9fe71a428bf5f2c78e54b', 'createTable tableName=books', 'add books table definition', 'EXECUTED', NULL, NULL, '5.0.1', '1991757644');

--  Changeset db.changelog-1.0.yaml::add-books-foreign-keys::christian.rivera
ALTER TABLE bookstore_database.books ADD CONSTRAINT fk_books_authors FOREIGN KEY (author_id) REFERENCES bookstore_database.authors (id);

ALTER TABLE bookstore_database.books ADD CONSTRAINT fk_books_categories FOREIGN KEY (category_id) REFERENCES bookstore_database.categories (id);

INSERT INTO bookstore_database.DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, MD5SUM, `DESCRIPTION`, COMMENTS, EXECTYPE, CONTEXTS, LABELS, LIQUIBASE, DEPLOYMENT_ID) VALUES ('add-books-foreign-keys', 'christian.rivera', 'db.changelog-1.0.yaml', NOW(), 4, '9:faaec8dc5bf8cad1c6455548fea05d25', 'addForeignKeyConstraint baseTableName=books, constraintName=fk_books_authors, referencedTableName=authors; addForeignKeyConstraint baseTableName=books, constraintName=fk_books_categories, referencedTableName=categories', '', 'EXECUTED', NULL, NULL, '5.0.1', '1991757644');

--  Changeset db.changelog-1.0.yaml::default-author-record::christian.rivera
--  insert default author record for testing
INSERT INTO bookstore_database.authors (name, fullname) VALUES ('John', 'Code With John');

INSERT INTO bookstore_database.DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, MD5SUM, `DESCRIPTION`, COMMENTS, EXECTYPE, CONTEXTS, LABELS, LIQUIBASE, DEPLOYMENT_ID) VALUES ('default-author-record', 'christian.rivera', 'db.changelog-1.0.yaml', NOW(), 5, '9:05da347d9dcecbe8a3f708286257f17d', 'insert tableName=authors', 'insert default author record for testing', 'EXECUTED', NULL, NULL, '5.0.1', '1991757644');

--  Changeset db.changelog-1.0.yaml::default-category-record::christian.rivera
--  insert default category record for testing
INSERT INTO bookstore_database.categories (name, `description`) VALUES ('Software Development', 'Software Development and Computer Science');

INSERT INTO bookstore_database.DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, MD5SUM, `DESCRIPTION`, COMMENTS, EXECTYPE, CONTEXTS, LABELS, LIQUIBASE, DEPLOYMENT_ID) VALUES ('default-category-record', 'christian.rivera', 'db.changelog-1.0.yaml', NOW(), 6, '9:3e4fc817a517230c9ebb9471591ac9fc', 'insert tableName=categories', 'insert default category record for testing', 'EXECUTED', NULL, NULL, '5.0.1', '1991757644');

--  Changeset db.changelog-1.0.yaml::default-book-record::christian.rivera
--  insert default book record for testing
INSERT INTO books (title, description, rating, published_date, author_id, category_id)
VALUES ('Python Programming', 'Python Programming', 4, 2020, (SELECT id FROM authors WHERE name = 'John'),(SELECT id FROM categories WHERE name = 'Software Development'));

INSERT INTO bookstore_database.DATABASECHANGELOG (ID, AUTHOR, FILENAME, DATEEXECUTED, ORDEREXECUTED, MD5SUM, `DESCRIPTION`, COMMENTS, EXECTYPE, CONTEXTS, LABELS, LIQUIBASE, DEPLOYMENT_ID) VALUES ('default-book-record', 'christian.rivera', 'db.changelog-1.0.yaml', NOW(), 7, '9:1d33055300e3047bb72d6f5a7c953d85', 'sql', 'insert default book record for testing', 'EXECUTED', NULL, NULL, '5.0.1', '1991757644');

--  Release Database Lock
UPDATE bookstore_database.DATABASECHANGELOGLOCK SET `LOCKED` = 0, LOCKEDBY = NULL, LOCKGRANTED = NULL WHERE ID = 1;

