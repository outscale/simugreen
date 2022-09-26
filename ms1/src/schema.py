from marshmallow import Schema, fields, ValidationError

class OutputSchema(Schema):
    id = fields.Integer(required=True)
    output = fields.String(required=True)