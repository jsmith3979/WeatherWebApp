import mysql.connector
from flask import Flask, redirect, url_for, render_template, request, jsonify, make_response, session
import requests
from db_connection import create_connection
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime , timedelta
from functools import wraps

api_key = '30d4741c779ba94c470ca1f63045390a'

app = Flask(__name__)
app.config['SECRET_KEY'] = '52783f3c95c6405eac9fae2982b799d2'

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid'})
    return decorated

@app.route('/public')
def public():
    return 'for public'

@app.route('/auth')
@token_required
def auth():
    return 'JWT IS VERIFIED'

# declaring the methods that we are going to use which are get and post, get being used to get the data
# and then post to post the data onto the
@app.route('/', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # variables
    weather = None
    temp = None

    # if the request method is equal to post then we will request the form from the html which in this case
    # is city
    if request.method == 'POST':
        user_input = request.form['city']
        # we then use the 'user_input' which is the city to find the correct city for the weather
        weather_data = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={user_input}&units=metric&APPID={api_key}"
        )
        # if the user types in a city that is not in the data it will return an error
        if weather_data.json()['cod'] == '404':
            print("error city not found")
        else:
            # else it will return the weather and temp data
            weather = weather_data.json()['weather'][0]['main']
            temp = weather_data.json()['main']['temp']
        # we then render the weather data and temp data into the html allowing us to use it in our html code
    return render_template("index.html", weather=weather, temp=temp)

@app.route('/register', methods=['GET','POST'])
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
            # Execute the query and commit
            cursor.execute(sql, val)
            db.commit()
            # Redirect to home page or confirmation page
            return redirect('/')
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return "There was an issue adding the user to the database."
        finally:
            # Close the database connection
            cursor.close()
            db.close()

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_password = request.form.get('user_password')

        # Input validation
        if not user_name or not user_password:
            return "Please provide both a username and a password."

        # Check the database for the user
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

                # Create JWT token (with PyJWT 2.x syntax)
                token = jwt.encode({
                    'user_name': user_name,
                    'exp': datetime.utcnow() + timedelta(minutes=30)
                }, app.config['SECRET_KEY'], algorithm="HS256")

                # Store token in session
                session['token'] = token

                # Redirect to homepage
                return redirect(url_for('home'))
            else:
                return "Invalid username or password."
        else:
            return "Invalid username or password."

    return render_template("login.html")


if __name__ == '__main__':
    app.run()



