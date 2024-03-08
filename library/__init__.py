from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask(__name__)
app.config["SECRET_KEY"] = "91234jk12kjfk9243kjf939jfjk3lk23j2k"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
API = Api(app)
db = SQLAlchemy()
db.init_app(app)

from library import routes

from library.api import UserAPI, BookAPI, SectionAPI

API.add_resource(UserAPI, "/api/user", "/api/user/<int:user_id>")
API.add_resource(BookAPI, "/api/book","/api/book/<int:book_id>")
API.add_resource(SectionAPI, "/api/section","/api/section/<int:section_id>")
