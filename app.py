from flask import Flask, jsonify, request
from flask import render_template
import sqlite3

app = Flask(__name__)
DB_PATH = "orders.db"  # Path to your SQLite database file

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return "Customer Orders API is running!"
@app.route('/dashboard')
def dashboard():
    return render_template('index.html')

# 1. Get all customers
@app.route('/api/customers', methods=['GET'])
def get_all_customers():
    try:
        conn = get_db_connection()
        users = conn.execute("SELECT * FROM users_table").fetchall()
        conn.close()
        return jsonify([dict(user) for user in users]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Get customers with minimum cancelled order count
@app.route('/api/customers/orders', methods=['GET'])
def get_customers_by_order_count():
    try:
        min_orders = int(request.args.get('min_orders', 1))  # Default to 1 if not specified

        conn = get_db_connection()
        query = """
            SELECT u.*, COUNT(c.order_id) AS order_count
            FROM users_table u
            JOIN cancelled_orders c ON u.id = c.user_id
            GROUP BY u.id
            HAVING order_count >= ?
        """
        result = conn.execute(query, (min_orders,)).fetchall()
        conn.close()

        users = [dict(row) for row in result]
        return jsonify(users), 200

    except ValueError:
        return jsonify({"error": "Invalid value for 'min_orders'. Must be an integer."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. Get cancelled order details by specific order_id (instead of user_id)
@app.route('/api/orders/<int:order_id>/cancelled', methods=['GET'])
def get_cancelled_order_by_order_id(order_id):
    try:
        conn = get_db_connection()
        query = "SELECT * FROM cancelled_orders WHERE order_id = ?"
        order = conn.execute(query, (order_id,)).fetchone()
        conn.close()

        if not order:
            return jsonify({"message": f"No cancelled order found for order_id {order_id}"}), 404

        return jsonify(dict(order)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
