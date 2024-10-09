import json
import sqlite3

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from
# from flask_login import login_required

from back.BD_interface import BD_int

class Report(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'Successful retrieval of report fields',
                'examples': {
                    'application/json': {
                        'header_first': {'example_key': 'example_value'},
                        'header_second': {'example_key': 'example_value'}
                    }
                }
            },
            404: {
                'description': 'Report not found'
            }
        },
        'parameters': [
            {
                'name': 'file_id',
                'description': 'ID of the file to get report fields',
                'in': 'path',
                'type': 'string',  
                'required': True
            }
        ]
    })
    def get(self, file_id):
        with BD_int() as bd:
            report = bd.get_report(file_id)

        if not report:
            return {'message': 'Report not found'}, 404
        else:
            return jsonify(report) 


class HistoryClass(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'Successful retrieval of report history',
                'examples': {
                    'application/json': {
                        'history': [
                            {"file_id": 1, "filename": "file.exe"},
                            {"file_id": 2, "filename": "file.dll"}
                        ]
                    }
                }
            },
            404: {
                'description': 'History not found'
            }
        },
        'parameters': [
            {
                'name': 'username',
                'description': 'Username to get report history',
                'in': 'path',
                'type': 'string',
                'required': True
            }
        ]
    })
    def get(self, username):
        with BD_int() as bd:
            history = bd.get_history(username)

        if not history:
            return {'message': 'History not found'}, 404
        else:
            return jsonify(history)  


def init(app):
    api = Api(app)
    swagger = Swagger(app)
    api.add_resource(Report, '/api/report/<string:file_id>') 
    api.add_resource(HistoryClass, '/api/report_history/<string:username>')

