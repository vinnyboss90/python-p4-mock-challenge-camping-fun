#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request, g
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return '<h1>Hi, I\'m John</h1>'

class Campers(Resource):
    def get(self):
        campers = [camper.to_dict() for camper in Camper.query.all()]
        #[print(camper) for camper in campers]
        return make_response(jsonify(campers), 200)
    
    def post(self):
        """
        try:
            new_camper = Camper(
                name=request.get_json().get('name'),
                age=request.get_json().get('age')
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(jsonify(new_camper.to_dict()), 201)
        except IntegrityError as e:
            return make_response({'error': e}, 400)
        """
        try:
            new_camper = Camper(
                name=request.get_json().get('name'),
                age=request.get_json().get('age')
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(jsonify(new_camper.to_dict()), 201)
        except ValueError as e:
            return make_response({'errors': [str(e)]}, 400)
    
    
class CamperByID(Resource):
    
    def get(self, id):
        if camper := Camper.query.filter_by(id=id).first():
            return make_response(jsonify(camper.to_dict()), 200)
        return make_response({'error': 'Camper not found'}, 404)
    
    def patch(self, id):
        if camper := Camper.query.filter_by(id=id).first():
            json = request.get_json()
            try:
                
                for attr in json:
                    setattr(camper, attr, json.get(attr))
                db.session.add(camper)
                db.session.commit()
                return make_response(jsonify(camper.to_dict()), 202)
            except ValueError as e:
                return make_response({'errors': ['validation errors']}, 400)
        return make_response({'error': 'Camper not found'}, 404)
    
api.add_resource(Campers, '/campers')
api.add_resource(CamperByID, '/campers/<int:id>')

# Activity

class Activities(Resource):
    def get(self):
        activities = [activity.to_dict() for activity in Activity.query.all()]
        return make_response(jsonify(activities), 200)


class ActivityByID(Resource):
    def delete(self, id):
        if activity := Activity.query.filter_by(id=id).first():
            db.session.delete(activity)
            db.session.commit()
            return make_response({'message': 'Activity deleted'}, 204)
        return make_response({'error': 'Activity not found'}, 404)
    
class Signups(Resource):
    def post(self):
        try:
            signup = Signup(
                time=request.get_json().get('time'),
                activity_id=request.get_json().get('activity_id'),
                camper_id=request.get_json().get('camper_id')
            )
            db.session.add(signup)
            db.session.commit()
            return signup.to_dict(), 201
        except ValueError as e:
            return {"errors": ["validation errors"]}, 400

api.add_resource(Activities, '/activities')
api.add_resource(ActivityByID, '/activities/<int:id>')
api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
