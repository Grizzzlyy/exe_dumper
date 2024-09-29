from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from
import sqlite3

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

def get_db_connection():
    conn = sqlite3.connect('BD/files.db')
    conn.row_factory = sqlite3.Row  # gets strings as a dict
    return conn

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
            },
            {
                'name': 'required_fields',
                'description': 'List of fields to retrieve',
                'in': 'query',
                'type': 'array',
                'items': {
                    'type': 'string'
                },
                'required': True
            }
        ]
    })
    def get(self, file_id):
        """Retrieve specified fields from a report."""
        required_fields = request.args.getlist('required_fields')
        
        conn = get_db_connection()
        report = conn.execute('SELECT * FROM files WHERE id = ?', (file_id,)).fetchone()
        conn.close()

        if report is None:
            return {'message': 'Report not found'}, 404
        result = {field: report[field] for field in required_fields if field in report.keys()}

        return jsonify(result)

api.add_resource(Report, '/report/<string:file_id>')

if __name__ == '__main__':
    app.run(debug=True)
