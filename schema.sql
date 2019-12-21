DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS records;
DROP VIEW IF EXISTS records_view;

CREATE TABLE users(
    id UNSIGNED INT PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(20),
    phone VARCHAR(15) NOT NULL UNIQUE,
    password VARCHAR(50) NOT NULL,
    valid BOOLEAN DEFAULT 0 NOT NULL,
    admin BOOLEAN DEFAULT 0 NOT NULL
);

CREATE TABLE items(
    id UNSIGNED INT PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    quantity UNSIGNED INT NOT NULL DEFAULT 0
);


CREATE TABLE records(
    id UNSIGNED INT PRIMARY KEY AUTOINCREMENT,
    operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id UNSIGNED INT FOREIGN KEY REFERENCES users(id) ON UPDATE CASCADE ON DELETE SET NULL,
    operation SET("TOOK", "ADDED"),
    item_id UNSIGNED INT FOREIGN KEY REFERENCES item_info(id) ON UPDATE CASCADE ON DELETE SET NULL,
    quantity UNSIGNED INT NOT NULL
);

CREATE VIEW records_view AS SELECT records.id, records.operation_time, users.name AS user_name,
 records.operation, items.name AS item_name,
 records.quantity FROM records INNER JOIN users ON records.user_id=users.id INNER JOIN items ON records.item_id=items.id
 ORDER BY records.id DESC;
