DROP DATABASE IF EXISTS supplier_inventory;
CREATE DATABASE supplier_inventory;
USE supplier_inventory;

DROP TABLE IF EXISTS PriceHistory;
DROP TABLE IF EXISTS Stock;
DROP TABLE IF EXISTS Purchase;
DROP TABLE IF EXISTS Product;
DROP TABLE IF EXISTS Supplier;

CREATE TABLE Supplier (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(200),
    address VARCHAR(200)
);

CREATE TABLE Product (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) NOT NULL,
    category ENUM('food', 'Drinks', 'Chemicals') NOT NULL,
    unit DECIMAL(10, 2)
);

CREATE TABLE Purchase (
    purchase_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    purchase_date DATE NOT NULL,
    total_amount DECIMAL(10, 2),
    FOREIGN KEY (supplier_id) REFERENCES Supplier(supplier_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

CREATE TABLE PriceHistory (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    old_price DECIMAL(10, 2),
    new_price DECIMAL(10, 2) NOT NULL,
    change_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

CREATE TABLE Stock (
    stock_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL,
    last_updated DATE,
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

DROP TRIGGER IF EXISTS purchase_added;

DELIMITER //
CREATE TRIGGER purchase_added
AFTER INSERT ON Purchase
FOR EACH ROW
BEGIN
    UPDATE Stock
    SET quantity = quantity + NEW.quantity,
        last_updated = NEW.purchase_date
    WHERE product_id = NEW.product_id;
END //
DELIMITER ;

DROP PROCEDURE IF EXISTS new_supplier;

DELIMITER //
CREATE PROCEDURE new_supplier(
    IN supplier_name VARCHAR(100),
    IN supplier_contact VARCHAR(200),
    IN supplier_address VARCHAR(200)
)
BEGIN
    INSERT INTO Supplier (name, contact_info, address)
    VALUES (supplier_name, supplier_contact, supplier_address);
END //
DELIMITER ;

DROP FUNCTION IF EXISTS get_total_spent;

DELIMITER //
CREATE FUNCTION get_total_spent(target_supplier_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
    DECLARE total DECIMAL(10,2);
    SELECT SUM(total_amount) INTO total FROM Purchase WHERE supplier_id = target_supplier_id;
    RETURN IFNULL(total, 0);
END //
DELIMITER ;

INSERT INTO Supplier (name, contact_info, address) VALUES
('Karlsson Livs AB', 'karl.svensson@karlssonlivs.se', 'Storgatan 14, Karlskrona'),
('Dryckeshuset', '0455-321890', 'Landbrogatan 8, Ronneby'),
('Rengoring Plus', 'kontakt@rengoringplus.se', NULL),
('Andersson Food Supply', 'maria.a@anderssonfood.se', 'Hogabergsgatan 3, Karlskrona');

INSERT INTO Product (name, category, unit) VALUES
('Kycklingfile 1kg', 'food', 1.00),
('Apelsinjuice Tropicana', 'Drinks', 1.50),
('Ajax allrent 1.5L', 'Chemicals', 1.50),
('Jasminris 2kg', 'food', 2.00),
('Ramlosa citron 33cl', 'Drinks', 0.33),
('Farskost 500g', 'food', 0.50),
('Handdiskmedel Yes', 'Chemicals', 0.50);

INSERT INTO Stock (product_id, quantity, last_updated) VALUES
(1, 45.00, '2026-01-20'),
(2, 18.00, '2026-01-20'),
(3, 62.00, '2026-01-22'),
(4, 33.00, '2026-01-20'),
(5, 140.00, '2026-02-01'),
(6, 12.00, '2026-01-28'),
(7, 55.00, '2026-01-22');

INSERT INTO Purchase (supplier_id, product_id, quantity, purchase_date, total_amount) VALUES
(1, 1, 15.00, '2026-02-03', 1125.50),
(4, 4, 8.00, '2026-02-05', 239.20),
(2, 2, 24.00, '2026-02-10', 576.00),
(1, 6, 10.00, '2026-02-12', 349.90),
(3, 3, 18.00, '2026-02-18', 628.20),
(2, 5, 48.00, '2026-02-22', 432.00),
(4, 1, 12.00, '2026-02-28', 948.00),
(3, 7, 30.00, '2026-03-02', 447.00);

INSERT INTO PriceHistory (product_id, old_price, new_price, change_date) VALUES
(1, 69.90, 75.50, '2026-01-15'),
(1, 75.50, 79.90, '2026-02-20'),
(2, 22.90, 24.00, '2026-02-05'),
(4, 28.90, 29.90, '2026-01-30'),
(5, 8.50, 9.00, '2026-02-10');
