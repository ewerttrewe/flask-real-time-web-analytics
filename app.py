#standard imports
from dotenv import load_dotenv
import os
#3rd party imports
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
#app imports
from .users import CreateUserView, CreateEntryView, ListUsersSiteStatView



load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]

jwt = JWTManager(app)


api = Api(app)

api.add_resource(CreateEntryView, "/v1/api/entry/create")
api.add_resource(CreateUserView, "/v1/api/users/registration")
api.add_resource(ListUsersSiteStatView, "/v1/api/users/site-stats")

if __name__ == "__main__":
    app.run(debug=True)
