import mysql.connector
from flask import Flask, redirect, url_for, render_template, request, jsonify, session
import requests
from db_connection import create_connection
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps

api_key = '30d4741c779ba94c470ca1f63045390a'

app = Flask(__name__)
app.config['SECRET_KEY'] = '52783f3c95c6405eac9fae2982b799d2'

def generate_token(user_name, secret_key):
    return jwt.encode({
        'user_name': user_name,
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }, secret_key, algorithm="HS256")

def decode_token(token, secret_key):
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if not token:
            return redirect(url_for('login'))
        result = decode_token(token, app.config['SECRET_KEY'])
        if isinstance(result, dict) and 'error' in result:
            return redirect(url_for('login'))
        session['user_name'] = result.get('user_name')
        return func(*args, **kwargs)
    return decorated


# @app.route('/test_token')
# @token_required
# def test_token():
#     token = session.get('token')
#     if not token:
#         return jsonify({'error': 'No token found'}), 401
#
#     try:
#         decoded = decode_token(token, app.config['SECRET_KEY'])
#     except Exception as e:
#         return jsonify({'error': str(e)}), 400
#
#     # Extract the user_name from the decoded token
#     user_name = decoded.get('user_name', 'Unknown User')
#
#     return jsonify({'user_name': user_name})


@app.route('/', methods=['GET', 'POST'])
@token_required
def home():
    weather = None
    temp = None
    user_name = session.get('user_name', 'Unknown User')  # Get the user_name from session

    if request.method == 'POST':
        user_input = request.form['city']
        weather_data = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={user_input}&units=metric&APPID={api_key}"
        )
        data = weather_data.json()
        if data.get('cod') == '404':
            print("error city not found")
        else:
            weather = data['weather'][0]['main']
            temp = data['main']['temp']

    # Pass the user_name to the template
    return render_template("index.html", weather=weather, temp=temp, user_name=user_name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_password = request.form['user_password']

        db = create_connection()
        cursor = db.cursor()

        hashed_password = generate_password_hash(user_password)

        sql = "INSERT INTO users (user_name, user_password) VALUES (%s, %s)"
        val = (user_name, hashed_password)
        try:
            cursor.execute(sql, val)
            db.commit()
            return redirect('/')
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return "There was an issue adding the user to the database."
        finally:
            cursor.close()
            db.close()

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_password = request.form.get('user_password')

        if not user_name or not user_password:
            return "Please provide both a username and a password."

        db = create_connection()
        cursor = db.cursor()
        sql = "SELECT user_password FROM users WHERE user_name = %s"
        val = (user_name,)
        cursor.execute(sql, val)
        user = cursor.fetchone()

        if user:
            stored_hashed_password = user[0]

            if check_password_hash(stored_hashed_password, user_password):
                session['logged_in'] = True

                token = generate_token(user_name, app.config['SECRET_KEY'])
                session['token'] = token

                # Log the token for debugging
                print(f"Generated Token: {token}")

                return redirect(url_for('home'))
            else:
                return "Invalid username or password."
        else:
            return "Invalid username or password."

    return render_template("login.html")

@app.route('/test')
def test():
    return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True)  # Set debug=True for detailed error logs


