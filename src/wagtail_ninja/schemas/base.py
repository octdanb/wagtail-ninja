from ninja import Schema

class BaseSchema(Schema):

    class Config:
        arbitrary_types_allowed = True

