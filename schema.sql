DROP TABLE IF EXISTS Delivered;
DROP TABLE IF EXISTS ItemIn;
DROP TABLE IF EXISTS Ordered;
DROP TABLE IF EXISTS Piece;
DROP TABLE IF EXISTS Location;
DROP TABLE IF EXISTS Act;
DROP TABLE IF EXISTS Role;
DROP TABLE IF EXISTS DonatedBy;
DROP TABLE IF EXISTS PersonPhone;
DROP TABLE IF EXISTS Person;
DROP TABLE IF EXISTS Item;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS Popularity;

CREATE TABLE Category (
    mainCategory VARCHAR(50) NOT NULL,
    subCategory VARCHAR(50) NOT NULL,
    catNotes TEXT,
    PRIMARY KEY (mainCategory, subCategory)
);

CREATE TABLE Item (
    ItemID INT NOT NULL AUTO_INCREMENT,
    iDescription TEXT,
    photo VARCHAR(20), 
    color VARCHAR(20),
    isNew BOOLEAN DEFAULT TRUE,
    hasPieces BOOLEAN,
    material VARCHAR(50),
    mainCategory VARCHAR(50) NOT NULL,
    subCategory VARCHAR(50) NOT NULL,
    PRIMARY KEY (ItemID),
    FOREIGN KEY (mainCategory, subCategory) REFERENCES Category(mainCategory, subCategory)
);

CREATE TABLE Person (
    userName VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    PRIMARY KEY (userName)
);

CREATE TABLE PersonPhone (
    userName VARCHAR(50) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    PRIMARY KEY (userName, phone),
    FOREIGN KEY (userName) REFERENCES Person(userName)
);

CREATE TABLE DonatedBy (
    ItemID INT NOT NULL,
    userName VARCHAR(50) NOT NULL,
    donateDate DATE NOT NULL,
    PRIMARY KEY (ItemID, userName),
    FOREIGN KEY (ItemID) REFERENCES Item(ItemID),
    FOREIGN KEY (userName) REFERENCES Person(userName)
);

CREATE TABLE Role (
    roleID VARCHAR(20) NOT NULL,
    rDescription VARCHAR(100),
    PRIMARY KEY (roleID)
);

CREATE TABLE Act (
    userName VARCHAR(50) NOT NULL,
    roleID VARCHAR(20) NOT NULL,
    PRIMARY KEY (userName, roleID),
    FOREIGN KEY (userName) REFERENCES Person(userName),
    FOREIGN KEY (roleID) REFERENCES Role(roleID)
);

CREATE TABLE Location (
    roomNum INT NOT NULL,
    shelfNum INT NOT NULL, 
    shelf VARCHAR(20),
    shelfDescription VARCHAR(200),
    PRIMARY KEY (roomNum, shelfNum)
);

CREATE TABLE Piece (
    ItemID INT NOT NULL,
    pieceNum INT NOT NULL,
    pDescription VARCHAR(200),
    length INT NOT NULL, 
    width INT NOT NULL,
    height INT NOT NULL,
    roomNum INT NOT NULL,
    shelfNum INT NOT NULL,
    pNotes TEXT,
    PRIMARY KEY (ItemID, pieceNum),
    FOREIGN KEY (ItemID) REFERENCES Item(ItemID),
    FOREIGN KEY (roomNum, shelfNum) REFERENCES Location(roomNum, shelfNum)
);

CREATE TABLE Ordered (
    orderID INT NOT NULL AUTO_INCREMENT,
    orderDate DATE NOT NULL,
    orderNotes VARCHAR(200),
    supervisor VARCHAR(50) NOT NULL,
    client VARCHAR(50) NOT NULL,
    PRIMARY KEY (orderID),
    FOREIGN KEY (supervisor) REFERENCES Person(userName),
    FOREIGN KEY (client) REFERENCES Person(userName)
);

CREATE TABLE ItemIn (
    ItemID INT NOT NULL,
    orderID INT NOT NULL,
    found BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (ItemID, orderID),
    FOREIGN KEY (ItemID) REFERENCES Item(ItemID),
    FOREIGN KEY (orderID) REFERENCES Ordered(orderID)
);

CREATE TABLE Delivered (
    userName VARCHAR(50) NOT NULL,
    orderID INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    PRIMARY KEY (userName, orderID),
    FOREIGN KEY (userName) REFERENCES Person(userName),
    FOREIGN KEY (orderID) REFERENCES Ordered(orderID)
);

CREATE TABLE Popularity (
    category VARCHAR(255) NOT NULL,
    subcategory VARCHAR(255) NOT NULL,
    order_count INTEGER DEFAULT 0,
    PRIMARY KEY (category, subcategory)
);



INSERT INTO Role (roleID, rDescription) VALUES ('1', 'Staff');
INSERT INTO Role (roleID, rDescription) VALUES ('2', 'Volunteer');
INSERT INTO Role (roleID, rDescription) VALUES ('3', 'Client');
INSERT INTO Role (roleID, rDescription) VALUES ('4', 'Donor');

-- INSERT INTO Person (userName, password, fname, lname, email) VALUES ('jdoe', 'password123', 'John', 'Doe', 'jdoe@nyu.edu');
-- INSERT INTO Person (userName, password, fname, lname, email) VALUES ('asmith', 'securepass', 'Alice', 'Smith', 'asmith@nyu.edu');
-- INSERT INTO Person (userName, password, fname, lname, email) VALUES ('bwhite', 'mypassword', 'Bob', 'White', 'bwhite@nyu.edu');
-- INSERT INTO Person (userName, password, fname, lname, email) VALUES ('cgreen', 'adminpass', 'Cathy', 'Green', 'cgreen@nyu.edu');
-- INSERT INTO Person (userName, password, fname, lname, email) VALUES ('jblack', 'blackpass', 'Jack', 'Black', 'jblack@nyu.edu');

INSERT INTO Person (userName, password, fname, lname, email) VALUES ('jdoe', 'scrypt:32768:8:1$Emw9ijaouAHok9Lr$98ca4b4dbafdad06e357763a428e062a7b42da012558f6ff6267a2032c9092ccfa0aaac15456ab132776da19d9a435cc1868038bc8458995707a89fc91155ab3', 'John', 'Doe', 'jdoe@nyu.edu');
INSERT INTO Person (userName, password, fname, lname, email) VALUES ('asmith', 'scrypt:32768:8:1$ygQhFvjXjxEwsXDO$bfecc7147ad6e275b20ca75f6e404e2858abda27e08c49f13f352d74b54f311f7befa2c62e47d2da8527c57f6ba1b32b25ada8dc859d4706494ef04497082c06', 'Alice', 'Smith', 'asmith@nyu.edu');
INSERT INTO Person (userName, password, fname, lname, email) VALUES ('bwhite', 'scrypt:32768:8:1$ldImAWJ7vSMy7dI6$94221e817ee18213230f7ac133999c24b70c026708b7da383203ed15df4cfd602b06f7314bbce04e5de18a405220d1365716cdc60293d0c87b052749a1dfcf2a', 'Bob', 'White', 'bwhite@nyu.edu');
INSERT INTO Person (userName, password, fname, lname, email) VALUES ('cgreen', 'scrypt:32768:8:1$fBXb2DhdgXHBJOX2$58f6a68e7b814600dab17f3a3b6b190326e2fc3c4e81ea3174da6ee4498a373d016a0226c01b29f5a65b431299432c3632aa0b0a969d6a17eb8115c0efe63397', 'Cathy', 'Green', 'cgreen@nyu.edu');
INSERT INTO Person (userName, password, fname, lname, email) VALUES ('jblack', 'scrypt:32768:8:1$KO1aSH1pt8YSMBWt$1e4ae69af9735778ef70ccd354a4f990993449f468b0bd87e9842f8eda322a040b2ec32e389b681fcd5e8cface2eaa9fbd8a1d415abc0ca9027b1c77f9e347b4', 'Jack', 'Black', 'jblack@nyu.edu');
INSERT INTO Person (userName, password, fname, lname, email) VALUES ('admin1', 'scrypt:32768:8:1$adminHash123$5e8dbb7f8ad0309e1ed830891f292b64d98ec918ff0ec0c5098f4d5b0b9fbe4f4a5b5c60b9436670fd0ec2b12d875f6c244d12db2d360b74e6c918e13e65d8ea', 'Admin', 'User', 'admin1@example.com');
INSERT INTO Person (userName, password, fname, lname, email) VALUES ('volunteer2', 'scrypt:32768:8:1$volunteerHash123$e7bf2bde88f0111f5d7c9d6b96a75cb95e6c0b36509c9e66b4a82d3b22b0b8f45ec8a4a15d93962f403fbaf678e593cc45f8e8a4b6d31035f5d91809c7589d37', 'Volunteer', 'Two', 'volunteer2@example.com');

INSERT INTO PersonPhone (userName, phone) VALUES ('jdoe', '123-456-7890');
INSERT INTO PersonPhone (userName, phone) VALUES ('asmith', '987-654-3210');
INSERT INTO PersonPhone (userName, phone) VALUES ('bwhite', '555-123-4567');
INSERT INTO PersonPhone (userName, phone) VALUES ('cgreen', '555-765-4321');
INSERT INTO PersonPhone (userName, phone) VALUES ('jblack', '666-987-1234');
INSERT INTO PersonPhone (userName, phone) VALUES ('admin1', '111-111-1111');
INSERT INTO PersonPhone (userName, phone) VALUES ('volunteer2', '222-222-2222');

INSERT INTO Act (userName, roleID) VALUES ('jdoe', '3');
INSERT INTO Act (userName, roleID) VALUES ('asmith', '4');
INSERT INTO Act (userName, roleID) VALUES ('bwhite', '2');
INSERT INTO Act (userName, roleID) VALUES ('cgreen', '1');
INSERT INTO Act (userName, roleID) VALUES ('jblack', '4');
INSERT INTO Act (userName, roleID) VALUES ('admin1', '1');
INSERT INTO Act (userName, roleID) VALUES ('volunteer2', '2');

INSERT INTO Category (mainCategory, subCategory, catNotes) VALUES ('Cookware', 'Frying Pan', 'Used in kitchens');
INSERT INTO Category (mainCategory, subCategory, catNotes) VALUES ('Furniture', 'Dining Table', 'Dining room furniture');
INSERT INTO Category (mainCategory, subCategory, catNotes) VALUES ('Electronics', 'Laptop', 'For computing needs');
INSERT INTO Category (mainCategory, subCategory, catNotes) VALUES ('Furniture', 'Chair', 'Used in living rooms and dining areas');
INSERT INTO Category (mainCategory, subCategory, catNotes) VALUES ('Electronics', 'Gaming Console Set', 'A set including a console and a controller');

INSERT INTO Item (ItemID, mainCategory, subCategory, iDescription, photo, color, isNew, hasPieces, material) VALUES (101, 'Furniture', 'Dining Table', 'A beautiful dining table set', 'dining_table.jpg', 'Brown', TRUE, TRUE, 'Wood');
INSERT INTO Item (ItemID, mainCategory, subCategory, iDescription, photo, color, isNew, hasPieces, material) VALUES (102, 'Cookware', 'Frying Pan', 'Non-stick frying pan', 'frying_pan.jpg', 'Black', FALSE, FALSE, 'Metal');
INSERT INTO Item (ItemID, mainCategory, subCategory, iDescription, photo, color, isNew, hasPieces, material) VALUES (103, 'Electronics', 'Laptop', 'High-performance laptop', 'laptop.jpg', 'Silver', TRUE, FALSE, 'Aluminum');

INSERT INTO DonatedBy (ItemID, userName, donateDate) VALUES (101, 'asmith', '2023-12-10');
INSERT INTO DonatedBy (ItemID, userName, donateDate) VALUES (102, 'asmith', '2023-12-11');
INSERT INTO DonatedBy (ItemID, userName, donateDate) VALUES (103, 'jblack', '2023-12-15');

INSERT INTO Location (roomNum, shelfNum, shelf, shelfDescription) VALUES (1, 1, 'A', 'Main storage area');
INSERT INTO Location (roomNum, shelfNum, shelf, shelfDescription) VALUES (1, 2, 'B', 'Secondary storage');
INSERT INTO Location (roomNum, shelfNum, shelf, shelfDescription) VALUES (2, 1, 'C', 'Kitchen storage shelf');
INSERT INTO Location (roomNum, shelfNum, shelf, shelfDescription) VALUES (3, 1, 'D', 'Electronics room shelf');
INSERT INTO Location (roomNum, shelfNum, shelf, shelfDescription) VALUES (20, 1, 'Holding', 'Holding location for delivery preparation');

INSERT INTO Piece (ItemID, pieceNum, pDescription, length, width, height, roomNum, shelfNum, pNotes) VALUES (101, 1, 'Dining table top', 200, 100, 75, 1, 1, 'Large wooden table');
INSERT INTO Piece (ItemID, pieceNum, pDescription, length, width, height, roomNum, shelfNum, pNotes) VALUES (101, 2, 'Dining chair', 50, 50, 90, 1, 2, 'Comfortable chair');
INSERT INTO Piece (ItemID, pieceNum, pDescription, length, width, height, roomNum, shelfNum, pNotes) VALUES (102, 1, 'Frying pan', 30, 30, 5, 2, 1, 'Non-stick frying pan stored in kitchen shelf');
INSERT INTO Piece (ItemID, pieceNum, pDescription, length, width, height, roomNum, shelfNum, pNotes) VALUES (103, 1, 'Laptop', 35, 25, 2, 3, 1, 'High-performance laptop stored in electronics room');

INSERT INTO Ordered (orderID, orderDate, orderNotes, supervisor, client) VALUES (12345, '2024-01-15', 'Requested delivery', 'cgreen', 'jdoe');
INSERT INTO Ordered (orderID, orderDate, orderNotes, supervisor, client) VALUES (12346, '2024-01-16', 'Requested express shipping', 'cgreen', 'jdoe');

INSERT INTO ItemIn (ItemID, orderID, found) VALUES (101, 12345, TRUE);
INSERT INTO ItemIn (ItemID, orderID, found) VALUES (102, 12346, FALSE);

INSERT INTO Delivered (orderID, userName, date, status) VALUES (12345, 'bwhite', '2024-01-20', 'Delivered');
INSERT INTO Delivered (orderID, userName, date, status) VALUES (12346, 'cgreen', '2024-01-21', 'In Transit');