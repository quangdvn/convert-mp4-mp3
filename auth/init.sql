CREATE DATABASE convert_auth;

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT null UNIQUE,
  password VARCHAR(255) NOT NULL
)

INSERT INTO users (email, password) VALUES ('test@gmail.com', '123456')