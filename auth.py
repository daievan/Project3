import mysql.connector
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, jsonify, session
)
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role


def create_auth_blueprint(login_manager: LoginManager):
    bp = Blueprint('auth', __name__, url_prefix='/auth')

    @login_manager.user_loader
    def load_user(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            'SELECT p.userName AS username, p.password AS password, a.roleID AS role '
            'FROM Person p '
            'LEFT JOIN Act a ON p.userName = a.userName '
            'WHERE p.userName = %s', 
            (user_id,)
        )
        user = cursor.fetchone()
        if user is None:
            return None
        return User(user_id=user['username'], username=user['username'], role=user['role'])
    
    @bp.route('/register', methods=('GET', 'POST'))
    def register():
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT roleID, rDescription FROM Role")
        roles = cursor.fetchall()

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            phone = request.form['phone']
            role = request.form['role']

            error = None

            cursor.execute("SELECT 1 FROM Person WHERE userName = %s", (username,))
            if cursor.fetchone():
                error = f"User {username} is already registered."

            cursor.execute("SELECT 1 FROM Role WHERE roleID = %s", (role,))
            if not cursor.fetchone():
                error = f"Invalid role: {role}. Please select a valid role."

            if error is None:
                try:
                    cursor.execute(
                        "INSERT INTO Person (userName, password, fname, lname, email) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (username, generate_password_hash(password), first_name, last_name, email),
                    )
                    cursor.execute(
                        "INSERT INTO PersonPhone (userName, phone) VALUES (%s, %s)",
                        (username, phone)
                    )
                    cursor.execute(
                        "INSERT INTO Act (userName, roleID) VALUES (%s, %s)",
                        (username, role)
                    )
                    db.commit()
                except mysql.connector.Error as e:
                    error = f"An error occurred: {e}"
                else:
                    return redirect(url_for("auth.login"))

            flash(error)

        return render_template('auth/register.html', roles=roles)

    @bp.route('/login', methods=('GET', 'POST'))
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('auth.index'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            db = get_db()
            cursor = db.cursor(dictionary=True)
            error = None

            cursor.execute(
                'SELECT p.userName AS username, p.password AS password, a.roleID AS role '
                'FROM Person p '
                'LEFT JOIN Act a ON p.userName = a.userName '
                'WHERE p.userName = %s', 
                (username,)
            )
            user = cursor.fetchone()

            if user is None:
                error = 'Non-existing username.'
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'

            if error is None:
                wrapped_user = User(user_id=user['username'], username=user['username'], role=user['role'])
                login_user(wrapped_user)
                return redirect(url_for('auth.index'))

            flash(error)

        return render_template('auth/login.html')

    @bp.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('auth.login'))

    @bp.route('/index', methods=('GET', 'POST'))
    @login_required
    def index():
        return render_template('auth/index.html')

    @bp.route('/find_single_item', methods=('GET', 'POST'))
    @login_required
    def find_single_item():
        locations = None
        error = None

        if request.method == 'POST':
            itemID = request.form['itemID']
            db = get_db()
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute(
                    """
                    SELECT 
                        p.pieceNum,
                        l.roomNum,
                        l.shelfNum,
                        l.shelfDescription
                    FROM Piece p
                    JOIN Location l ON p.roomNum = l.roomNum AND p.shelfNum = l.shelfNum
                    WHERE p.ItemID = %s
                    """,
                    (itemID,)
                )
                locations = cursor.fetchall()

                if not locations:
                    error = f"No locations found for Item ID {itemID}."
            except mysql.connector.Error as e:
                error = f"An error occurred: {e}"

        return render_template('auth/find_single_item.html', locations=locations, error=error)

    @bp.route('/find_order_items', methods=('GET', 'POST'))
    @login_required
    def find_order_items():
        items_with_locations = None
        error = None

        if request.method == 'POST':
            orderID = request.form['orderID']
            db = get_db()
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute(
                    """
                    SELECT 
                        i.ItemID,
                        i.iDescription AS itemDescription,
                        p.pieceNum,
                        l.roomNum,
                        l.shelfNum,
                        l.shelfDescription
                    FROM ItemIn ii
                    JOIN Item i ON ii.ItemID = i.ItemID
                    LEFT JOIN Piece p ON i.ItemID = p.ItemID
                    LEFT JOIN Location l ON p.roomNum = l.roomNum AND p.shelfNum = l.shelfNum
                    WHERE ii.orderID = %s
                    """,
                    (orderID,)
                )
                items_with_locations = cursor.fetchall()

                if not items_with_locations:
                    error = f"No items found for Order ID {orderID}."
            except mysql.connector.Error as e:
                error = f"An error occurred: {e}"

        return render_template('auth/find_order_items.html', items_with_locations=items_with_locations, error=error)
    @bp.route('/accept_donation', methods=('GET', 'POST'))
    def accept_donation():
        if not current_user.is_authenticated or current_user.role != '1':  
            flash('Only staff members can accept donations.')
            return redirect(url_for('auth.index'))

        db = get_db()
        cursor = db.cursor()

        if request.method == 'POST':
            donor_id = request.form['donor_id']
            main_category = request.form['mainCategory']
            sub_category = request.form['subCategory']
            item_description = request.form['item_description']
            photo_filename = request.form['photo_filename']
            material = request.form['material']
            color = request.form['color']
            is_new = request.form['is_new']
            has_pieces = request.form['has_pieces']
            donation_date = request.form['donation_date']

            cursor.execute('SELECT userName FROM Act WHERE userName = %s AND roleID = "4"', (donor_id,))
            donor = cursor.fetchone()
            if not donor:
                flash('The specified donor is not registered as a donor.')
                return redirect(url_for('auth.accept_donation'))

            cursor.execute(
                'INSERT INTO Item (mainCategory, subCategory, iDescription, photo, color, isNew, hasPieces, material) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                (main_category, sub_category, item_description, photo_filename, color, is_new, has_pieces, material)
            )
            item_id = cursor.lastrowid

            cursor.execute(
                'INSERT INTO DonatedBy (ItemID, userName, donateDate) VALUES (%s, %s, %s)',
                (item_id, donor_id, donation_date)
            )

            # piece_count = 1 if has_pieces == "0" else int(request.form.get('piece_count', 1))
            # piece_count = 2
            piece_count = int(request.form.get('piece_count'))
            for i in range(1, piece_count + 1):
                piece_description = request.form.get(f'piece_{i}_description', f'Piece {i}')
                room_num = request.form[f'piece_{i}_room_num']
                shelf_num = request.form[f'piece_{i}_shelf_num']
                length = request.form.get(f'piece_{i}_length', 0)
                width = request.form.get(f'piece_{i}_width', 0)
                height = request.form.get(f'piece_{i}_height', 0)
                notes = request.form.get(f'piece_{i}_notes', '')

                cursor.execute(
                    'INSERT INTO Piece (ItemID, pieceNum, pDescription, length, width, height, roomNum, shelfNum, pNotes) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (item_id, i, piece_description, length, width, height, room_num, shelf_num, notes)
                )

            db.commit()
            flash('Donation successfully recorded.')
            return redirect(url_for('auth.index'))

        cursor.execute('SELECT DISTINCT mainCategory FROM Category')
        main_categories = [row[0] for row in cursor.fetchall()]

        return render_template('auth/accept_donation.html', main_categories=main_categories)


    @bp.route('/get_subcategories/<main_category>', methods=['GET'])
    def get_subcategories(main_category):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT DISTINCT subCategory FROM Category WHERE mainCategory = %s",
            (main_category,)
        )
        subcategories = cursor.fetchall()
        return jsonify([sub['subCategory'] for sub in subcategories])

    @bp.route('/start_order', methods=('GET', 'POST'))
    def start_order():
        if not current_user.is_authenticated or current_user.role != '1':  # Check if user is staff
            flash('Only staff members can start orders.')
            return redirect(url_for('auth.index'))

        db = get_db()
        cursor = db.cursor(dictionary=True)

        if request.method == 'POST':
            client_username = request.form['client_username']
            order_notes = request.form.get('order_notes', '')  # Optional field

            # Validate client
            cursor.execute(
                'SELECT userName FROM Act WHERE userName = %s AND roleID = "3"', (client_username,)
            )
            client = cursor.fetchone()
            if not client:
                flash('The specified username is not a valid client.')
                return redirect(url_for('auth.start_order'))

            # Insert the new order
            cursor.execute(
                'INSERT INTO Ordered (orderDate, orderNotes, supervisor, client) '
                'VALUES (CURDATE(), %s, %s, %s)',
                (order_notes, current_user.username, client_username)
            )
            order_id = cursor.lastrowid
            db.commit()

            # Save the order ID in session
            session['order_id'] = order_id
            flash(f'Order started successfully. Order ID: {order_id}')
            return redirect(url_for('auth.index'))

        return render_template('auth/start_order.html')
    
    @bp.route('/add_to_order', methods=('GET', 'POST'))
    def add_to_order():
        if not current_user.is_authenticated or current_user.role != '1': 
            flash('Only staff members can add to orders.')
            return redirect(url_for('auth.index'))

        db = get_db()
        cursor = db.cursor()

        if request.method == 'POST':
            order_id = session.get('order_id')  
            item_id = request.form.get('item_id')

            if not order_id:
                flash('No active order found. Start a new order first.')
                return redirect(url_for('auth.start_order'))

            cursor.execute(
                'INSERT INTO ItemIn (ItemID, orderID, found) VALUES (%s, %s, FALSE)',
                (item_id, order_id)
            )

            db.commit()
            flash('Item added to the order successfully!')
            return redirect(url_for('auth.add_to_order'))

        cursor.execute('SELECT DISTINCT mainCategory FROM Category')
        main_categories = [row[0] for row in cursor.fetchall()]

        return render_template('auth/add_to_order.html', main_categories=main_categories)


    @bp.route('/get_items/<main_category>/<sub_category>', methods=['GET'])
    def get_items(main_category, sub_category):
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT ItemID, iDescription, material, color 
            FROM Item 
            WHERE mainCategory = %s AND subCategory = %s AND ItemID NOT IN (
                SELECT ItemID FROM ItemIn
            )
            """,
            (main_category, sub_category)
        )
        items = cursor.fetchall()
        return jsonify(items)
    @bp.route('/prepare_order', methods=('GET', 'POST'))
    def prepare_order():
        if not current_user.is_authenticated or current_user.role != '1':  # Check if user is staff
            flash('Only staff members can prepare orders.')
            return redirect(url_for('auth.index'))

        db = get_db()
        cursor = db.cursor(dictionary=True)

        if request.method == 'POST':
            search_type = request.form['search_type']
            search_value = request.form['search_value']

            items = []

            if search_type == 'order_number':  # Search by order number
                cursor.execute(
                    "SELECT Item.ItemID, Item.iDescription, Piece.roomNum, Piece.shelfNum, Piece.pNotes "
                    "FROM Item "
                    "JOIN Piece ON Item.ItemID = Piece.ItemID "
                    "WHERE Item.ItemID IN (SELECT ItemID FROM ItemIn WHERE orderID = %s AND found = 0)",
                    (search_value,)
                )
                items = cursor.fetchall()

                cursor.execute(
                    "UPDATE Piece "
                    "SET roomNum = 20, shelfNum = 1, pNotes = 'Ready for delivery' "
                    "WHERE ItemID IN (SELECT ItemID FROM ItemIn WHERE orderID = %s AND found = 0)",
                    (search_value,)
                )
                cursor.execute(
                    "UPDATE ItemIn "
                    "SET found = TRUE "
                    "WHERE orderID = %s AND found = 0",
                    (search_value,)
                )
            elif search_type == 'client_username':  # Search by client username
                cursor.execute(
                    "SELECT orderID FROM Ordered WHERE client = %s",
                    (search_value,)
                )
                orders = cursor.fetchall()

                if not orders:
                    flash('No orders found for the specified client.')
                    return redirect(url_for('auth.prepare_order'))

                order_ids = [order['orderID'] for order in orders]

                cursor.execute(
                    "SELECT Item.ItemID, Item.iDescription, Piece.roomNum, Piece.shelfNum, Piece.pNotes "
                    "FROM Item "
                    "JOIN Piece ON Item.ItemID = Piece.ItemID "
                    "WHERE Item.ItemID IN (SELECT ItemID FROM ItemIn WHERE orderID IN (%s) AND found = 0)" % 
                    ','.join(['%s'] * len(order_ids)),
                    tuple(order_ids)
                )
                items = cursor.fetchall()


                cursor.execute(
                    "UPDATE Piece "
                    "SET roomNum = 20, shelfNum = 1, pNotes = 'Ready for delivery' "
                    "WHERE ItemID IN (SELECT ItemID FROM ItemIn WHERE orderID IN (%s) AND found = 0)" % 
                    ','.join(['%s'] * len(order_ids)),
                    tuple(order_ids)
                )
                cursor.execute(
                    "UPDATE ItemIn "
                    "SET found = TRUE "
                    "WHERE orderID IN (%s) AND found = 0" % ','.join(['%s'] * len(order_ids)),
                    tuple(order_ids)
                )

            db.commit()

            if not items:
                flash('No items found for the given order or client, or all items are already prepared.')
            else:
                flash('Order prepared successfully. Items moved to the holding location.')

            return redirect(url_for('auth.prepare_order'))

        return render_template('auth/prepare_order.html')
    
    @bp.route('/my_orders', methods=['GET'])
    def my_orders():
        if not current_user.is_authenticated:
            flash('Please log in to view your orders.')
            return redirect(url_for('auth.login'))

        db = get_db()
        cursor = db.cursor(dictionary=True)

        user_role = current_user.role
        user_name = current_user.username
        orders = []

        if user_role == '3':  # Client
            cursor.execute(
                """
                SELECT o.orderID, o.orderDate, o.orderNotes, i.ItemID, i.iDescription, ii.found
                FROM Ordered o
                JOIN ItemIn ii ON o.orderID = ii.orderID
                JOIN Item i ON ii.ItemID = i.ItemID
                WHERE o.client = %s
                """, 
                (user_name,)
            )
            orders = cursor.fetchall()

        elif user_role == '1':  # Staff
            cursor.execute(
                """
                SELECT o.orderID, o.orderDate, o.orderNotes, d.userName AS deliverer
                FROM Ordered o
                LEFT JOIN Delivered d ON o.orderID = d.orderID
                WHERE o.supervisor = %s
                """, 
                (user_name,)
            )
            orders = cursor.fetchall()

        elif user_role == '2':  # Volunteer
            cursor.execute(
                """
                SELECT o.orderID, o.orderDate, o.orderNotes, d.date AS deliveryDate, d.status
                FROM Delivered d
                JOIN Ordered o ON d.orderID = o.orderID
                WHERE d.userName = %s
                """, 
                (user_name,)
            )
            orders = cursor.fetchall()

        return render_template('auth/my_orders.html', orders=orders, role=user_role)
    return bp