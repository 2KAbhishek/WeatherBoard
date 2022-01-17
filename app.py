import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '2KAbhishek'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


def delete_city(city_name):
    city_obj = City.query.filter_by(name=city_name).first()
    db.session.delete(city_obj)
    db.session.commit()


@app.route('/', methods=['GET', 'POST'])
def index():
    cities = City.query.all()
    city_names = [city.name for city in cities]

    if request.method == 'POST':
        new_city = request.form.get('city')

        if new_city not in city_names:
            new_city_obj = City(name=new_city)
            db.session.add(new_city_obj)
            db.session.commit()

            city_names.append(new_city)
        else:
            flash('{} already added!'.format(new_city), 'info')

    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=271d1234d3f497eed5b1d80a07b3fcd1'

    weather_data = []

    for city_name in city_names:
        r = requests.get(url.format(city_name)).json()

        if r['cod'] != 200:
            flash('No data for {}'.format(city_name), 'danger')
            delete_city(city_name)
        else:
            weather = {
                'city': city_name,
                'temperature': r['main']['temp'],
                'description': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon'],
            }
            weather_data.append(weather)

    return render_template('index.html', weather_data=weather_data)


@ app.route('/delete/<string:city_name>', methods=['POST'])
def delete(city_name):
    delete_city(city_name)
    flash('{} removed!'.format(city_name), 'success')
    return redirect(url_for('index'))
