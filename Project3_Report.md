# Project3_Report

## 1. Languages and Frameworks Used

**Languages**: Python,HTML, CSS, SQL 

**Frameworks/Libraries**:

​	•	Flask 

​	•	Flask-Login

​	•	Flask-MySQLdb 

​	•	Werkzeug (Password hashing)

## 2.The main queries for each of the features

### 1.

```sql
SELECT p.userName AS username, p.password AS password
FROM Person p 
WHERE p.userName = %s;
```

### 2.

```sql
SELECT p.pieceNum, l.roomNum, l.shelfNum, l.shelfDescription 
FROM Piece p 
JOIN Location l ON p.roomNum = l.roomNum AND p.shelfNum = l.shelfNum 
WHERE p.ItemID = %s;
```

### 3.

```sql
SELECT i.ItemID, i.iDescription AS itemDescription, p.pieceNum, l.roomNum, l.shelfNum, l.shelfDescription 
FROM ItemIn ii 
JOIN Item i ON ii.ItemID = i.ItemID 
LEFT JOIN Piece p ON i.ItemID = p.ItemID 
LEFT JOIN Location l ON p.roomNum = l.roomNum AND p.shelfNum = l.shelfNum 
WHERE ii.orderID = %s;
```

### 4.

**Validate the donor**

```sql
SELECT userName FROM Act WHERE userName = %s AND roleID = "4";
```

**Insert new item:**

```sql
INSERT INTO Item (mainCategory, subCategory, iDescription, photo, color, isNew, hasPieces, material) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
```

**Insert donor information:**

```sql
INSERT INTO DonatedBy (ItemID, userName, donateDate) 
VALUES (%s, %s, %s);
```

**Insert pieces:**

```sql
INSERT INTO Piece (ItemID, pieceNum, pDescription, length, width, height, roomNum, shelfNum, pNotes) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
```

### 5.

**Validate the client:**

```sql
SELECT userName FROM Act WHERE userName = %s AND roleID = "3";
```

**Insert new order:**

```sql
INSERT INTO Ordered (orderDate, orderNotes, supervisor, client) 
VALUES (CURDATE(), %s, %s, %s);
```

### 6.

**Fetch available items by category and subcategory:**

```sql
SELECT ItemID, iDescription, material, color 
FROM Item 
WHERE mainCategory = %s AND subCategory = %s 
AND ItemID NOT IN (SELECT ItemID FROM ItemIn);
```

**Add item to the current order:**

```sql
INSERT INTO ItemIn (ItemID, orderID, found) 
VALUES (%s, %s, FALSE);
```

### 7.

#### 1.**Search by Order Number**

**Fetch items and their details for the given order number where items have not been marked as “found”:**

```sql
SELECT Item.ItemID, Item.iDescription, Piece.roomNum, Piece.shelfNum, Piece.pNotes
FROM Item
JOIN Piece ON Item.ItemID = Piece.ItemID
WHERE Item.ItemID IN (
    SELECT ItemID FROM ItemIn WHERE orderID = %s AND found = 0
);
```

**Update the location of the items in the order to “holding location” (roomNum = 20, shelfNum = 1):**

```sql
UPDATE Piece
SET roomNum = 20, shelfNum = 1, pNotes = 'Ready for delivery'
WHERE ItemID IN (
    SELECT ItemID FROM ItemIn WHERE orderID = %s AND found = 0
);
```

**Mark the items in the ItemIn table as “found”:**

```sql
UPDATE ItemIn
SET found = TRUE
WHERE orderID = %s AND found = 0;
```



#### **2. Search by Client Username**

**Fetch all order IDs for the given client:**

```sql
SELECT orderID FROM Ordered WHERE client = %s;
```

**Fetch items and their details for all orders belonging to the client where items have not been marked as “found”:**

```sql
SELECT Item.ItemID, Item.iDescription, Piece.roomNum, Piece.shelfNum, Piece.pNotes
FROM Item
JOIN Piece ON Item.ItemID = Piece.ItemID
WHERE Item.ItemID IN (
    SELECT ItemID FROM ItemIn WHERE orderID IN (%s) AND found = 0
);
```

**Update the location of items across all the client’s orders to “holding location”:**

```sql
UPDATE Piece
SET roomNum = 20, shelfNum = 1, pNotes = 'Ready for delivery'
WHERE ItemID IN (
    SELECT ItemID FROM ItemIn WHERE orderID IN (%s) AND found = 0
);
```

**Mark the items in the ItemIn table as “found” for all orders belonging to the client:**

```sql
UPDATE ItemIn
SET found = TRUE
WHERE orderID IN (%s) AND found = 0;
```

### 8.

#### 1.staff

**Query for Supervise Orders**

```sql
SELECT o.orderID, o.orderDate, o.orderNotes
FROM Ordered o
WHERE o.supervisor = %s;
```

**Query for Deliver Orders**

```sql
SELECT o.orderID, o.orderDate, o.orderNotes
FROM Ordered o
JOIN Delivered d ON o.orderID = d.orderID
WHERE d.userName = %s;
```

#### 2.client

**Query for Client Orders**

```sql
SELECT o.orderID, o.orderDate, o.orderNotes, i.ItemID, i.iDescription, ii.found
FROM Ordered o
JOIN ItemIn ii ON o.orderID = ii.orderID
JOIN Item i ON ii.ItemID = i.ItemID
WHERE o.client = %s;
```

#### 3.volunteer

**Query for Volunteer Delivery Orders**

```sql
SELECT o.orderID, o.orderDate, o.orderNotes, d.date AS deliveryDate, d.status
FROM Delivered d
JOIN Ordered o ON d.orderID = o.orderID
WHERE d.userName = %s;
```

## 3.**Lessons Learned from the Project**

**Panzhu Dai:**

In this project, I learned the importance of establishing a foundational framework before diving into the details. Building a clear and well-structured overall framework is essential for managing the project’s complexity. To ensure functionality and maintain organization, I created separate code files to handle different features and functionalities.

When encountering issues during code execution, I utilized breakpoints at different locations in the code to systematically debug and identify the problems. This iterative process of debugging and refining helped me improve the quality and reliability of the project.



## 4.**Contribution of Team Members**

**Panzhu Dai:**

​	•	**Required Application Features**: Worked on features 1–4.

​	•	**Additional Features**: Worked on features 5–8.

