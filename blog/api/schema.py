from ninja import Schema


class LoginSchemaIn(Schema):
    username: str
    password: str


class LoginSchemaOut(Schema):
    access_token: str
    refresh_token: str


class RefeshSchemaOut(Schema):
    access_token: str


class ChangePasswordSchemaIn(Schema):
    old_password: str
    new_password: str