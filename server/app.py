#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# Route to get all restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])


# Route to get a single restaurant by ID
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    return jsonify(restaurant.to_dict())


# Route to delete a restaurant by ID
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    db.session.delete(restaurant)
    db.session.commit()
    return make_response('', 204)


# Route to get all pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])


# Route to create a RestaurantPizza
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    restaurant_id = data.get('restaurant_id')
    pizza_id = data.get('pizza_id')
    price = data.get('price')

    if not restaurant_id or not pizza_id or not price:
        return make_response(jsonify({"error": "Missing data"}), 400)

    if not (1 <= price <= 30):
        return make_response(jsonify({"error": "Price must be between 1 and 30"}), 400)

    new_restaurant_pizza = RestaurantPizza(
        restaurant_id=restaurant_id,
        pizza_id=pizza_id,
        price=price
    )

    db.session.add(new_restaurant_pizza)
    db.session.commit()

    return jsonify(new_restaurant_pizza.to_dict()), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
