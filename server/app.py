#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


class RestaurantClass(Resource):
    def get(self):
        restaurant_list = [
            restaurant.to_dict(rules=("-restaurant_pizzas",))
            for restaurant in Restaurant.query.all()
        ]
        return make_response(restaurant_list, 200)


api.add_resource(RestaurantClass, "/restaurants")


class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).one_or_none()
        if restaurant:
            return make_response(restaurant.to_dict(), 200)
        else:
            return make_response({"error": "Restaurant not found"}, 404)

    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).one_or_none()
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            return make_response({}, 204)
        else:
            return make_response({"error": "Restaurant not found"}, 404)


api.add_resource(RestaurantById, "/restaurants/<int:id>")


class PizzaClass(Resource):
    def get(self):
        pizzas = [pizza.to_dict(only=("id", "ingredients", "name"))
                  for pizza in Pizza.query.all()]
        return make_response(pizzas, 200)


api.add_resource(PizzaClass, "/pizzas")


class RestaurantPizzasClass(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_res_pizza = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(new_res_pizza)
            db.session.commit()

            return make_response(new_res_pizza.to_dict(), 201)
        except (KeyError, ValueError):
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(RestaurantPizzasClass, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)