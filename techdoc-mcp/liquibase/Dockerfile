FROM liquibase/liquibase:latest

ARG NEO4J_EXTENSION_VERSION=5.0.4

USER root

# Automatically install the PostgreSQL JDBC driver via LPM
RUN lpm add postgresql --global

# Download Liquibase Neo4j Extension into Liquibase classpath
ADD https://github.com/liquibase/liquibase-neo4j/releases/download/v${NEO4J_EXTENSION_VERSION}/liquibase-neo4j-${NEO4J_EXTENSION_VERSION}-full.jar \
    /liquibase/lib/liquibase-neo4j.jar

RUN chown liquibase:liquibase /liquibase/lib/liquibase-neo4j.jar

USER liquibase