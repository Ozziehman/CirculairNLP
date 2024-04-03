@echo off

:: Put path to neo4j plugins folder here
cd /d "A:\Neo4j\neo4j-community-5.18.1-windows\neo4j-community-5.18.1\plugins"
if not exist "apoc-5.18.0-core.jar" (
    curl -L -O https://github.com/neo4j/apoc/releases/download/5.18.0/apoc-5.18.0-core.jar
)

:: Put path to neo4j bin folder here
cd /d "A:\Neo4j\neo4j-community-5.18.1-windows\neo4j-community-5.18.1\bin"
neo4j console