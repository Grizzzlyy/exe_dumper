from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger, swag_from
import parse_exe

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

# Mock database for demonstration purposes
mock_db = {
    "1": {
        "PE_header": "PE header data for report 1",
        "DOS_header": "DOS header data for report 1",
        "other_field": "Other data"
    },
    "2": {
        "PE_header": "PE header data for report 2",
        "DOS_header": "DOS header data for report 2",
        "other_field": "Other data"
    }
}

class Report(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'Successful retrieval of report fields',
                'examples': {
                    'application/json': {
                        'PE_header': 'PE header data for report 1',
                        'DOS_header': 'DOS header data for report 1'
                    }
                }
            },
            404: {
                'description': 'Report not found'
            }
        },
        'parameters': [
            {
                'name': 'report_id',
                'description': 'ID of the report',
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
    def get(self, report_id):
        """Retrieve specified fields from a report."""
        required_fields = request.args.getlist('required_fields')
        
        # Fetch the report from the mock database
        report = mock_db.get(report_id)
        
        if not report:
            return {'message': 'Report not found'}, 404
        
        # Filter the report to return only the requested fields
        result = {field: report[field] for field in required_fields if field in report}
        
        return jsonify(result)

api.add_resource(Report, '/report/<string:report_id>')

if __name__ == '__main__':
    app.run(debug=True)
