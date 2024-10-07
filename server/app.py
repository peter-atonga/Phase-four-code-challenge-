#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


# Resource: GET /heroes
class HeroesList(Resource):
    def get(self):
        heroes = Hero.query.all()
        heroes_list = [hero.to_dict() for hero in heroes]
        return heroes_list, 200


# Resource: GET /heroes/<id>
class HeroDetail(Resource):
    def get(self, hero_id):
        hero = Hero.query.get(hero_id)
        if hero:
            hero_data = hero.to_dict()
            # Serialize hero_powers
            hero_powers = [hp.to_dict() for hp in hero.hero_powers]
            hero_data['hero_powers'] = hero_powers
            return hero_data, 200
        else:
            return {"error": "Hero not found"}, 404


# Resource: GET /powers
class PowersList(Resource):
    def get(self):
        powers = Power.query.all()
        powers_list = [power.to_dict() for power in powers]
        return powers_list, 200


# Resource: GET /powers/<id>
class PowerDetail(Resource):
    def get(self, power_id):
        power = Power.query.get(power_id)
        if power:
            return power.to_dict(), 200
        else:
            return {"error": "Power not found"}, 404


# Resource: PATCH /powers/<id>
class PowerUpdate(Resource):
    def patch(self, power_id):
        power = Power.query.get(power_id)
        if not power:
            return {"error": "Power not found"}, 404

        data = request.get_json()
        description = data.get('description')

        if description is not None:
            if len(description)<20:
                return {"errors":["validation errors"]},400
            else:
                power.description = description

        try:
            db.session.commit()
            return power.to_dict(), 200
        except ValueError as ve:
            db.session.rollback()
            return {"errors": [str(ve)]}, 400
        except Exception as e:
            db.session.rollback()
            return {"errors": ["An unexpected error occurred"]}, 500


# Resource: POST /hero_powers
class HeroPowerCreate(Resource):
    def post(self):
        data = request.get_json()
        strength = data.get('strength')
        hero_id = data.get('hero_id')
        power_id = data.get('power_id')

        # Validate presence of required fields
        if not all([strength, hero_id, power_id]):
            return {"errors": ["Missing required fields: strength, hero_id, power_id"]}, 400

        # Validate strength value
        if strength not in ['Strong', 'Weak', 'Average']:
            return {"errors": ["validation errors"]}, 400

        # Check if Hero exists
        hero = Hero.query.get(hero_id)
        if not hero:
            return {"errors": ["Hero not found"]}, 404

        # Check if Power exists
        power = Power.query.get(power_id)
        if not power:
            return {"errors": ["Power not found"]}, 404

        # Create new HeroPower
        new_hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)

        try:
            db.session.add(new_hero_power)
            db.session.commit()
            # Serialize the new HeroPower including hero and power details
            hero_power_data = new_hero_power.to_dict()
            return hero_power_data, 200
        except ValueError as ve:
            db.session.rollback()
            return {"errors": [str(ve)]}, 400
        except Exception as e:
            db.session.rollback()
            return {"errors": ["An unexpected error occurred"]}, 500


# Adding Resources to the API
api.add_resource(HeroesList, '/heroes')
api.add_resource(HeroDetail, '/heroes/<int:hero_id>')
api.add_resource(PowersList, '/powers')
api.add_resource(PowerDetail, '/powers/<int:power_id>')
api.add_resource(PowerUpdate, '/powers/<int:power_id>')
api.add_resource(HeroPowerCreate, '/hero_powers')


# Root Route
@app.route('/')
def index():
    return '<h1>Superheroes API</h1>', 200


# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request"}), 400


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500


# Run the app
if __name__ == '__main__':
    app.run(port=5555, debug=True)
