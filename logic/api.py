import json
import sqlite3
from os import getenv
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from

from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from back.parse_file import get_chunk
# from flask_login import login_required

from back.BD_interface import BD_int

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Your API",
        "description": "API documentation",
        "version": "1.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter JWT token like: Bearer <token>"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

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
        username = get_jwt_identity()
        with BD_int() as bd:
            report = bd.get_report(username,file_id)

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
        }
    })
    @jwt_required()
    def get(self):
        username = get_jwt_identity()
        with BD_int() as bd:
            history = bd.get_history(username)

        if not history:
            return {'message': 'History not found'}, 404
        else:
            return jsonify(history)  

class some(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'some_awesome',
                'examples': {
                    'application/json': {
                        'chunk': '4D 5A 50 00 02 00 00 00 04 00 0F 00 FF FF 00 00'
                    }
                }
            },
            404: {
                'description': 'History not found'
            }
        },
        'parameters': [
            {
                'name': 'file_idx',
                'description': 'ID of the file to get report fields',
                'in': 'path',
                'type': 'integer',  
                'required': True
            },
            {
                'name': 'chunk_number',
                'description': 'Number of chunk you wants to get',
                'in': 'path',
                'type': 'integer',  
                'required': True
            }
        ]
    })
    @jwt_required()
    def get(self, file_idx, chunk_number):
        username = get_jwt_identity()
        with BD_int() as worker:
            file_name = worker.get_filename_by_idx(username,file_idx)
        if not file_name:
            return {'message': 'No such file'}, 404
        else:
            file_dir = getenv("UPLOADS_DIR")
            str_chunk = get_chunk(chunk_number, f"./{file_dir}/{username}/{file_name}")
            if not str_chunk:
                return{'message': 'Something wrong with chunk_number'},404

            return jsonify({'chunk': str_chunk})



def init(app):
    api = Api(app)
    swagger = Swagger(app, template=swagger_template)
    api.add_resource(Report,'/api/report/<string:file_id>') 
    api.add_resource(some,'/api/chunk/<int:file_idx>/<int:chunk_number>')
    api.add_resource(HistoryClass, '/api/report_history')
    app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY")

    jwt = JWTManager(app)
