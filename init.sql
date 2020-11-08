CREATE SCHEMA IF NOT EXISTS test_schema;
SET search_path TO test_schema;

CREATE TABLE IF NOT EXISTS test_schema.visited_urls (
    url varchar(50) PRIMARY KEY,
    first_symbols varchar(10),
    UNIQUE(url)
);