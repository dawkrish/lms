import datetime

import bcrypt
import werkzeug
from flask import make_response
from flask_restful import Resource, reqparse, fields, marshal_with
import json
from library import models, db

'''
    OUTPUT-STRCUTURES
'''
user_output = {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
}

book_output = {
    "id": fields.Integer,
    "name": fields.String,
    "author": fields.String,
    "content": fields.String,
    "section_id": fields.Integer
}
section_output = {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "books": fields.List(fields.Nested(book_output))
}

'''
    PARSERS
'''
user_parser = reqparse.RequestParser()
user_parser.add_argument("username")
user_parser.add_argument("email")
user_parser.add_argument("password")

book_parser = reqparse.RequestParser()
book_parser.add_argument("name")
book_parser.add_argument("author")
book_parser.add_argument("content")
book_parser.add_argument("section_id")
book_parser.add_argument("number_of_copies")

section_parser = reqparse.RequestParser()
section_parser.add_argument("name")
section_parser.add_argument("description")

'''
    ERRORS
'''


class NotFoundError(werkzeug.exceptions.HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)


class BusinessValidationError(werkzeug.exceptions.HTTPException):
    def __init__(self, status_code, error_code, error_message):
        message = {"error_code": error_code, "error_message": error_message}
        self.response = make_response(json.dumps(message), status_code)


'''
    API-RESOURCES
'''


class UserAPI(Resource):
    @marshal_with(user_output)
    def get(self, user_id):
        u = models.User.query.get(user_id)
        if u is None:
            raise NotFoundError(404)

        return u, 200

    def post(self):
        args = user_parser.parse_args()
        username = args.get("username")
        email = args.get("email")
        password = args.get("password")

        if username is None or username == "":
            raise BusinessValidationError(status_code=400, error_code="USER001", error_message="Username not provided")

        if email is None or email == "":
            raise BusinessValidationError(status_code=400, error_code="USER002", error_message="Email not provided")

        if password is None or password == "":
            raise BusinessValidationError(status_code=400, error_code="USER003", error_message="Password not provided")

        if models.User.query.filter(models.User.username == username).first() is not None:
            raise BusinessValidationError(status_code=400, error_code="USER004",
                                          error_message="Username already exists")

        if models.User.query.filter(models.User.email == email).first() is not None:
            raise BusinessValidationError(status_code=400, error_code="USER005",
                                          error_message="Email already exists")

        new_user = models.User(username=username, email=email,
                               password=bcrypt.hashpw(password.encode(), bcrypt.gensalt(10)).decode())
        db.session.add(new_user)
        db.session.commit()

        return f"Successfully created user with id -> {new_user.id}", 201

    @marshal_with(user_output)
    def put(self, user_id):
        if user_id == 1:
            raise BusinessValidationError(status_code=403, error_code="ADMIN001",
                                          error_message="Method not allowed for admin")

        u = models.User.query.get(user_id)
        if u is None:
            raise NotFoundError(404)

        args = user_parser.parse_args()
        username = args.get("username")
        email = args.get("email")
        password = args.get("password")

        if username is None or username == "":
            raise BusinessValidationError(status_code=400, error_code="USER001", error_message="Username not provided")

        if email is None or email == "":
            raise BusinessValidationError(status_code=400, error_code="USER002", error_message="Email not provided")

        if password is None or password == "":
            raise BusinessValidationError(status_code=400, error_code="USER003", error_message="Password not provided")

        if models.User.query.filter(models.User.username == username).first() is not None:
            raise BusinessValidationError(status_code=400, error_code="USER004",
                                          error_message="Username already exists")

        if models.User.query.filter(models.User.email == email).first() is not None:
            raise BusinessValidationError(status_code=400, error_code="USER005",
                                          error_message="Email already exists")

        u.username = username
        u.email = email
        u.password = bcrypt.hashpw(password.encode(), bcrypt.gensalt(10)).decode()
        db.session.commit()

        return u, 200

    def delete(self, user_id):
        if user_id == 1:
            raise BusinessValidationError(status_code=403, error_code="ADMIN001",
                                          error_message="Method not allowed for admin")
        u = models.User.query.get(user_id)
        if u is None:
            raise NotFoundError(404)

        db.session.delete(u)
        db.session.commit()
        return "Successfully delete the user", 200


class BookAPI(Resource):
    @marshal_with(book_output)
    def get(self, book_id):
        b = models.Book.query.get(book_id)
        if b is None:
            raise NotFoundError(404)

        return b, 200

    def post(self):

        args = book_parser.parse_args()

        name = args.get("name", None)
        author = args.get("author", None)
        content = args.get("content", None)
        section_id = args.get("section_id", None)
        number_of_copies = args.get("number_of_copies", None)
        number_of_copies = int(number_of_copies)

        if name is None or name == "":
            raise BusinessValidationError(status_code=400, error_code="BOOK001", error_message="Book Name not provided")

        if author is None or author == "":
            raise BusinessValidationError(status_code=400, error_code="BOOK002",
                                          error_message="Book Author not provided")

        if content is None or content == "":
            raise BusinessValidationError(status_code=400, error_code="BOOK003",
                                          error_message="Book Content not provided")

        if section_id is None or section_id == "":
            raise BusinessValidationError(status_code=400, error_code="BOOK004",
                                          error_message="Section ID not provided")

        if number_of_copies is None or number_of_copies == 0:
            raise BusinessValidationError(status_code=400, error_code="BOOK005",
                                          error_message="Number of Copies not provided")

        if models.Section.query.get(section_id) is None:
            raise BusinessValidationError(status_code=400, error_code="BOOK006",
                                          error_message="Section ID does not exist")

        for i in range(number_of_copies):
            new_book = models.Book(name=name, author=author, content=content, section_id=section_id)
            db.session.add(new_book)
        db.session.commit()

        return f"Successfully created {number_of_copies} books", 201

    @marshal_with(book_output)
    def put(self, book_id):
        b = models.Book.query.get(book_id)
        if b is None:
            raise NotFoundError(404)
        args = book_parser.parse_args()

        name = args.get("name", None)
        author = args.get("author", None)
        content = args.get("content", None)
        section_id = args.get("section_id", None)

        if name is None or name == "":
            raise BusinessValidationError(status_code=400, error_code="BOOK001", error_message="Book Name not provided")

        if author is None or author == "":
            raise BusinessValidationError(status_code=400, error_code="BOOK002",
                                          error_message="Book Author not provided")

        if content is None or content == "":
            raise BusinessValidationError(status_code=400, error_code="BOOK003",
                                          error_message="Book Content not provided")

        if section_id is None or section_id == "":
            raise BusinessValidationError(status_code=400, error_code="BOOK004",
                                          error_message="Section ID not provided")

        b.name = name
        b.author = author
        b.content = content
        b.section_id = section_id
        db.session.commit()

        return b, 200

    def delete(self, book_id):
        b = models.Book.query.get(book_id)
        if b is None:
            raise NotFoundError(404)

        db.session.delete(b)
        db.session.commit()
        return "Successfully delete the book", 200


class SectionAPI(Resource):
    @marshal_with(section_output)
    def get(self, section_id):
        s = models.Section.query.get(section_id)
        if s is None:
            raise NotFoundError(404)

        return s, 200

    def post(self):
        args = section_parser.parse_args()

        name = args.get("name", None)
        description = args.get("description", None)

        if name is None or name == "":
            raise BusinessValidationError(status_code=400, error_code="SECTION001",
                                          error_message="Section Name not provided")

        if description is None or description == "":
            raise BusinessValidationError(status_code=400, error_code="SECTION002",
                                          error_message="Section Description not provided")

        if models.Section.query.filter(models.Section.name == name).first() is not None:
            raise BusinessValidationError(status_code=400, error_code="SECTION003",
                                          error_message="Section Name already exists")

        new_section = models.Section(name=name, description=description, date_created=datetime.date.today())
        db.session.add(new_section)
        db.session.commit()

        return f"Successfully created user section id -> {new_section.id}", 201

    @marshal_with(section_output)
    def put(self, section_id):
        s = models.Section.query.get(section_id)
        if s is None:
            raise NotFoundError(404)

        args = section_parser.parse_args()

        name = args.get("name", None)
        description = args.get("description", None)

        if name is None or name == "":
            raise BusinessValidationError(status_code=400, error_code="SECTION001",
                                          error_message="Section Name not provided")

        if description is None or description == "":
            raise BusinessValidationError(status_code=400, error_code="SECTION002",
                                          error_message="Section Description not provided")

        if models.Section.query.filter(models.Section.name == name).first() is not None:
            raise BusinessValidationError(status_code=400, error_code="SECTION003",
                                          error_message="Section Name already exists")
        s.name = name
        s.description = description

        db.session.commit()
        return s, 200

    def delete(self, section_id):
        s = models.Section.query.get(section_id)
        if s is None:
            raise NotFoundError(404)

        db.session.delete(s)
        db.session.commit()
        return "Successfully delete the section and all the books of that section", 200
