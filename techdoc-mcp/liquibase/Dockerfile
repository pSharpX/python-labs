FROM liquibase/liquibase:latest

ARG NEO4J_EXTENSION_VERSION=5.0.4

USER root

# Automatically install the PostgreSQL JDBC driver via LPM
RUN lpm add postgresql --global
# Automatically install the Neo4j Plugin extension via LPM
#RUN curl -sL https://repo1.maven.org/maven2/org/reactivestreams/reactive-streams/1.0.4/reactive-streams-1.0.4.jar -o /liquibase/lib/reactive-streams.jar \
# && curl -sL https://repo1.maven.org/maven2/org/neo4j/driver/neo4j-java-driver/5.20.0/neo4j-java-driver-5.20.0.jar -o /liquibase/lib/neo4j-java-driver.jar
#RUN lpm add liquibase-neo4j --global

ADD https://github.com/liquibase/liquibase-neo4j/releases/download/v${NEO4J_EXTENSION_VERSION}/liquibase-neo4j-${NEO4J_EXTENSION_VERSION}-full.jar \
    /liquibase/lib/liquibase-neo4j.jar

RUN chown liquibase:liquibase /liquibase/lib/liquibase-neo4j.jar

# Download Neo4j Java Driver & Liquibase Neo4j Extension into Liquibase classpath
#RUN curl -sL https://repo1.maven.org/maven2/org/neo4j/driver/neo4j-java-driver/5.20.0/neo4j-java-driver-5.20.0.jar -o /liquibase/lib/neo4j-java-driver.jar \
# && curl -sL https://repo1.maven.org/maven2/org/liquibase/ext/liquibase-neo4j/4.29.0.1/liquibase-neo4j-4.29.0.1.jar -o /liquibase/lib/liquibase-neo4j.jar

USER liquibase