# Readme



## **Installation and Running**

**Follow these steps to set up and run the project:**

### **1. Initialize Environment**

```
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-mysqldb flask-login werkzeug
pip install mysql-connector-python
```

### **2. Database Configuration**

**Modify the following section in _ init_.py to match your database configuration:**

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 8889
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'Project3'
```

### **3. Run the project**

```
export FLASK_APP=__init__.py:create_app
flask init-db
flask run
```
