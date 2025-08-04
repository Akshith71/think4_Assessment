from flask import Flask, jsonify, request
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

# 3. Get all cancelled orders for a specific customer by user_id
@app.route('/api/customers/<int:user_id>/cancelled_orders', methods=['GET'])
def get_cancelled_orders_for_customer(user_id):
    try:
        conn = get_db_connection()
        query = "SELECT * FROM cancelled_orders WHERE user_id = ?"
        orders = conn.execute(query, (user_id,)).fetchall()
        conn.close()

        if not orders:
            return jsonify({"message": f"No cancelled orders found for user_id {user_id}"}), 404

        return jsonify([dict(order) for order in orders]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
