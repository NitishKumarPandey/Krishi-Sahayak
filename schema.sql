/*
    to create database
*/
CREATE DATABASE IF NOT EXISTS farm1_db;
USE farm1_db;


/*
    to create table
*/
CREATE TABLE IF NOT EXISTS farmer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    F_Firstname VARCHAR(255),
    F_Lastname VARCHAR(255),
    F_Email VARCHAR(255),
    F_Phone VARCHAR(15),
    F_Income FLOAT,
    F_Gender VARCHAR(10),
    F_Address TEXT,
    F_ContactNo VARCHAR(15)
);

CREATE TABLE IF NOT EXISTS farm (
    id INT AUTO_INCREMENT PRIMARY KEY,
    User_id INT,
    Farm_name VARCHAR(255),
    Location VARCHAR(255),
    Acre FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(id)
);

CREATE TABLE IF NOT EXISTS crop_allocation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    User_id INT,
    Farm_id INT,
    Crop_name VARCHAR(255),
    Area_allocated FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(id),
    FOREIGN KEY (Farm_id) REFERENCES farm(id)
);

CREATE TABLE IF NOT EXISTS seed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    User_id INT,
    Seed_name VARCHAR(255),
    Crop_name VARCHAR(255),
    Quantity FLOAT,
    Seed_price FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(id)
);

CREATE TABLE IF NOT EXISTS pesticide (
    id INT AUTO_INCREMENT PRIMARY KEY,
    User_id INT,
    Pesticide_name VARCHAR(255),
    Crop_name VARCHAR(255),
    Quantity FLOAT,
    Pesticide_price FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(id)
);

CREATE TABLE IF NOT EXISTS fertilizer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    User_id INT,
    Fertilizer_name VARCHAR(255),
    Crop_name VARCHAR(255),
    Quantity FLOAT,
    Fertilizer_price FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(id)
);

CREATE TABLE IF NOT EXISTS labour (
    id INT AUTO_INCREMENT PRIMARY KEY,
    User_id INT,
    Name VARCHAR(255),
    Salary FLOAT,
    Crop_name VARCHAR(255),
    FOREIGN KEY (User_id) REFERENCES farmer(id)
);

CREATE TABLE IF NOT EXISTS warehouse (
    id INT AUTO_INCREMENT PRIMARY KEY,
    User_id INT,
    Location VARCHAR(255),
    Capacity INT,
    FOREIGN KEY (User_id) REFERENCES farmer(id)
);

CREATE TABLE IF NOT EXISTS crop_market (
    id INT AUTO_INCREMENT PRIMARY KEY,
    User_id INT,
    Crop_name VARCHAR(255),
    Selling_price FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(id)
);
