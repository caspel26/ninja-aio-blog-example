from ninja import Schema


class LoginSchemaIn(Schema):
    username: str
    password: str


class LoginSchemaOut(Schema):
    access_token: str
    refresh_token: str