from flask import Flask
from flask_restful import Api
from .users import UsersRegistrationView
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
api = Api(app)


api.add_resource(UsersRegistrationView, "/api/users/registration")


if __name__ == "__main__":
    app.run(debug=True)
