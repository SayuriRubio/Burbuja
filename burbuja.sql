CREATE DATABASE if not exists burbuja;

use burbuja;

CREATE TABLE IF NOT EXISTS intento_orden(
	id INT auto_increment PRIMARY KEY,
    intento TEXT NOT NULL,
    res TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT current_timestamp
    );