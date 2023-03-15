# from flask import Flask
# from flask_restx import Api, Resource, fields
# from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
# from werkzeug.security import generate_password_hash, check_password_hash
#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'  # change this to your database connection string
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JWT_SECRET_KEY'] = 'secret'  # change this to your secret key
#
# db = SQLAlchemy(app)
# jwt = JWTManager(app)
# api = Api(app)
