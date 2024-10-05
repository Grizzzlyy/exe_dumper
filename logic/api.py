import json
import sqlite3

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from

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
                'description': 'file_id to get fields',
                'in': 'path',
                'type': 'string',
                'required': True
            }
        ]
    })
    def get(self, file_id):
        bd = BD_int()

        report = bd.get_report(file_id)

        if report is None:
            return {'message': 'Report not found'}, 404
        else:
            return report


def init(app):
    api = Api(app)
    swagger = Swagger(app)
    api.add_resource(Report, '/api/report/<string:file_id>')
