import click
from flask import current_app, g
import mysql.connector.cursor
from mysql.connector import Error
def get_db():
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config['MYSQL_HOST'],
                port=current_app.config['MYSQL_PORT'],
                user=current_app.config['MYSQL_USER'],
                password=current_app.config['MYSQL_PASSWORD'],
                database=current_app.config['MYSQL_DB']
            )
            g.db.row_factory = mysql.connector.cursor.MySQLCursorDict
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            g.db = None
    if g.db is None:
        print("Database connection failed!")
    else:
        print("Database connection successful!")
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        sql_script = f.read().decode('utf8')
        try:
            for statement in sql_script.split(';'):
                statement = statement.strip()
                if statement:  
                    print(f"Executing SQL: {statement}")
                    with db.cursor() as cursor:  
                        cursor.execute(statement)
            db.commit()  
        except mysql.connector.Error as e:
            print(f"Error executing SQL: {e}")
            db.rollback()

def update_popularity(category, subcategory):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        INSERT INTO Popularity (category, subcategory, order_count)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE
        order_count = order_count + 1
        """,
        (category, subcategory),
    )
    db.commit()

def get_popular_categories(limit = 5):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT category, subcategory, order_count
        FROM Popularity
        ORDER BY order_count DESC
        LIMIT %s;
        """,
        (limit,)
    )
    return cursor.fetchall()

def update_order(userName, orderID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    result = cursor.execute(
        """
        INSERT INTO Delivered (userName, orderID)
        VALUES (%s, %s)
        """,
        (userName, orderID),
    ).fetchone()
    return result is not None

def user_can_update(userName, orderID, role):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if role == 1: # Staff
        cursor.execute(
            """
            SELECT 1
            FROM Ordered
            WHERE orderID = %s AND supervisor = %s
            """,
            (orderID, userName),
        )
    elif role == 2: # Volunteer
        cursor.execute(
            """
            SELECT 1
            FROM Delivered
            WHERE orderID = %s AND userName = %s
            """,
            (orderID, userName),
        )
    else:
        return False
    return cursor.fetchone() is not None

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)