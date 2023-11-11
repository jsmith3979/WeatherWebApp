from flask import Flask, redirect, url_for, render_template,request
import requests

api_key = '30d4741c779ba94c470ca1f63045390a'

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    weather = None
    temp = None

    if request.method == 'POST':
        user_input = request.form['city']
        weather_data = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={user_input}&units=imperial&APPID={api_key}"
        )
        # if the user types in a city that is not in the data it will return an error
        if weather_data.json()['cod'] == '404':
            print("error city not found")
        else:
        # else it will return the weather and temp data
            weather = weather_data.json()['weather'][0]['main']
            temp = weather_data.json()['main']['temp']
        # we then render the weather data and temp data
    return render_template("index.html",weather=weather, temp=temp, content= [weather, temp])

if __name__ == '__main__':
    app.run()