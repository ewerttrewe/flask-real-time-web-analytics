#standard imports
from dotenv import load_dotenv
import os
#3rd party imports
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
#app imports
from .users import UsersRegistrationView, UserProtectedView



load_dotenv()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["headers"]

jwt = JWTManager(app)


api = Api(app)

api.add_resource(UserProtectedView, "/api/users/protected")
api.add_resource(UsersRegistrationView, "/api/users/registration")

if __name__ == "__main__":
    app.run(debug=True)
