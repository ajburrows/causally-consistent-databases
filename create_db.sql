CREATE DATABASE server1;
CREATE DATABASE server2;


USE server1;
CREATE TABLE dependencies(
    id INT AUTO_INCREMENT PRIMARY KEY,
    dependency_key VARCHAR(255)
);
CREATE TABLE data_centers(
    id INT AUTO_INCREMENT PRIMARY KEY,
    dc_port INT
);
CREATE TABLE messages(
    dependency_key VARCHAR(255) PRIMARY KEY,
    content TEXT
);

USE server2;
CREATE TABLE dependencies(
    id INT AUTO_INCREMENT PRIMARY KEY,
    dependency_key VARCHAR(255)
);
CREATE TABLE data_centers(
    id INT AUTO_INCREMENT PRIMARY KEY,
    dc_port INT
);
CREATE TABLE messages(
    dependency_key VARCHAR(255) PRIMARY KEY,
    content TEXT
);