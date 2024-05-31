from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pizzeria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Pizza(db.Model):
    __tablename__ = 'pizzas'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    ingredients: Mapped[str] = mapped_column(db.String(200), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)

def init_db():
    db.create_all()
    if not Pizza.query.first():
        pizzas = [
            {'name': 'Margherita', 'ingredients': 'Tomato, Mozzarella, Basil', 'price': 8.99},
            {'name': 'Pepperoni', 'ingredients': 'Tomato, Mozzarella, Pepperoni', 'price': 9.99},
            {'name': 'Hawaiian', 'ingredients': 'Tomato, Mozzarella, Ham, Pineapple', 'price': 10.99},
        ]
        for pizza in pizzas:
            new_pizza = Pizza(name=pizza['name'], ingredients=pizza['ingredients'], price=pizza['price'])
            db.session.add(new_pizza)
        db.session.commit()
        print("Initial pizzas added to the database.")

@app.route('/')
def home():
    weather = get_weather('Kyiv')  # Replace 'Kyiv' with your city
    recommendation = get_pizza_recommendation(weather)
    return render_template('index.html', weather=weather, recommendation=recommendation)

@app.route('/menu')
def menu():
    sort_by = request.args.get('sort', 'asc')
    if sort_by == 'asc':
        pizzas = Pizza.query.order_by(Pizza.price).all()
    elif sort_by == 'desc':
        pizzas = Pizza.query.order_by(Pizza.price.desc()).all()
    return render_template('menu.html', pizzas=pizzas, sort_by=sort_by)

@app.route('/add', methods=['GET', 'POST'])
def add_dish():
    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form['ingredients']
        price = request.form['price']
        new_pizza = Pizza(name=name, ingredients=ingredients, price=price)
        db.session.add(new_pizza)
        db.session.commit()
        return redirect(url_for('menu'))
    return render_template('add_dish.html')

def get_weather(city):
    api_key = '70820c384a1d4a538ec63035243105' 
    url = f'http://api.weatherapi.com/v1/current.json?key={api_key}&q=70820c384a1d4a538ec63035243105'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_pizza_recommendation(weather):
    if weather:
        temp = weather['main']['temp']
        description = weather['weather'][0]['description']
        if temp < 0:
            return "It's freezing outside! Warm up with a hot Pepperoni pizza."
        elif temp < 15:
            return "It's a bit chilly. How about a Margherita to keep you warm?"
        elif temp < 25:
            return "Nice weather for a Hawaiian pizza!"
        else:
            return "It's hot outside! A light Veggie pizza would be perfect."
    return "Can't get the weather data right now. Enjoy any pizza you like!"

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)