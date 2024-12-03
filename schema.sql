CREATE DATABASE IF NOT EXISTS farm1_db;
USE farm1_db;

CREATE TABLE IF NOT EXISTS farmer (
    User_id VARCHAR(255) PRIMARY KEY,
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
    Farm_id INT AUTO_INCREMENT PRIMARY KEY,
    User_id VARCHAR(255),
    Farm_name VARCHAR(255),
    Location VARCHAR(255),
    Area FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(User_id)
);

CREATE TABLE IF NOT EXISTS crop_allocation (
    Allocation_id INT AUTO_INCREMENT PRIMARY KEY,
    User_id VARCHAR(255),
    Farm_id INT,
    Crop_name VARCHAR(255),
    Area_allocated FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(User_id),
    FOREIGN KEY (Farm_id) REFERENCES farm(Farm_id)
);

CREATE TABLE IF NOT EXISTS seed (
    Seed_id INT AUTO_INCREMENT PRIMARY KEY,
    User_id VARCHAR(255),
    Crop_name VARCHAR(255),
    Quantity INT,
    Seed_price FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(User_id)
);

CREATE TABLE IF NOT EXISTS pesticide (
    Pesticide_id INT AUTO_INCREMENT PRIMARY KEY,
    User_id VARCHAR(255),
    Crop_name VARCHAR(255),
    Quantity INT,
    Pesticide_price FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(User_id)
);

CREATE TABLE IF NOT EXISTS fertilizer (
    Fertilizer_id INT AUTO_INCREMENT PRIMARY KEY,
    User_id VARCHAR(255),
    Crop_name VARCHAR(255),
    Quantity INT,
    Fertilizer_price FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(User_id)
);

CREATE TABLE IF NOT EXISTS labour (
    Labour_id INT AUTO_INCREMENT PRIMARY KEY,
    User_id VARCHAR(255),
    Name VARCHAR(255),
    Role VARCHAR(255),
    Salary FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(User_id)
);

CREATE TABLE IF NOT EXISTS warehouse (
    Warehouse_id INT AUTO_INCREMENT PRIMARY KEY,
    User_id VARCHAR(255),
    Location VARCHAR(255),
    Capacity INT,
    FOREIGN KEY (User_id) REFERENCES farmer(User_id)
);

CREATE TABLE IF NOT EXISTS crop_market (
    Market_id INT AUTO_INCREMENT PRIMARY KEY,
    User_id VARCHAR(255),
    Crop_name VARCHAR(255),
    Selling_price FLOAT,
    FOREIGN KEY (User_id) REFERENCES farmer(User_id)
);
