-- Delete the tables if they exist
DROP TABLE IF EXISTS Transaction;
DROP TABLE IF EXISTS Payment_Method;
DROP TABLE IF EXISTS Truck;
DROP TABLE IF EXISTS uploaded_files;

-- Create the tables
CREATE TABLE Payment_Method (
    payment_method_id SMALLINT PRIMARY KEY,
    payment_method VARCHAR(10)
);

CREATE TABLE Truck (
    truck_id SMALLINT PRIMARY KEY,
    truck_name VARCHAR(255),
    truck_description TEXT,
    has_card_reader BOOLEAN,
    fsa_rating SMALLINT
);


CREATE TABLE Transaction (
    transaction_id BIGINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    truck_id SMALLINT NOT NULL,
    payment_method_id SMALLINT NOT NULL,
    total FLOAT NOT NULL,
    at TIMESTAMP NOT NULL,

    FOREIGN KEY (truck_id) REFERENCES Truck(truck_id),
    FOREIGN KEY (payment_method_id) REFERENCES Payment_Method(payment_method_id)
) AUTO_INCREMENT = 1;


CREATE TABLE uploaded_files (
    filename_id SMALLINT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    filename VARCHAR(100) NOT NULL
);


-- Insert data into the tables
INSERT INTO Payment_Method (payment_method_id, payment_method) VALUES
(1, 'cash'),
(2, 'card');

INSERT INTO Truck (truck_id, truck_name, truck_description, has_card_reader, fsa_rating) VALUES
(1, 'Burrito Madness', 'An authentic taste of Mexico.', TRUE, 4),
(2, 'Kings of Kebabs', 'Locally-sourced meat cooked over a charcoal grill.', TRUE, 2),
(3, 'Cupcakes by Michelle', 'Handcrafted cupcakes made with high-quality, organic ingredients.', TRUE, 5),
(4, 'Hartmann''s Jellied Eels', 'A taste of history with this classic English dish.', TRUE, 4),
(5, 'Yoghurt Heaven', 'All the great tastes, but only some of the calories!', TRUE, 4),
(6, 'SuperSmoothie', 'Pick any fruit or vegetable, and we''ll make you a delicious, healthy, multi-vitamin shake. Live well; live wild.', FALSE, 3);
