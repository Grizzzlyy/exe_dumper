import json
import sqlite3
from os import getenv
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
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
    @jwt_required()
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
                'token': 'your generatet token'
            },
            {
                'name': 'username',
                'description': 'Username to get report history',
                'in': 'path',
                'type': 'string',
                'required': True
            }
        ]
    })
    @jwt_required()
    def get(self, username):
        with BD_int() as bd:
            history = bd.get_history(username)

        if not history:
            return {'message': 'History not found'}, 404
        else:
            return jsonify(history)


class CunkFile(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'Successful retrieval of report fields',
                'examples': {
                    'application/json': {
                        '4D 5A 50 00 02 00 00 00 04 00 0F 00 FF FF 00 00 B8 00 00 00 00 00 00 00 40 00 1A 00 00 00 00 00'
                    }
                }
            },
            404: {
                'description': 'Report not found'
            }
        },
        'parameters': [
            {
                ''
            },
            {
                'name': 'file_name',
                'description': 'name of file to get chunk from it',
                'in': 'path',
                'type': 'string',
                'required': True
            }
        ]
    })
    def get():
        pass


def init(app):
    api = Api(app)
    swagger = Swagger(app)
    api.add_resource(Report, '/api/report/<string:file_id>')
    api.add_resource(HistoryClass, '/api/report_history/<string:username>')
    app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY")
    jwt = JWTManager(app)
